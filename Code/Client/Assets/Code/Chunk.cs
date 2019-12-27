using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Chunk {

    public GameObject me;
    public MeshRenderer meshRenderer;
    public MeshFilter meshFilter;

    private Vector2 chunkPos;
    private byte[,,] blocks;

    private List<Vector3> verts = new List<Vector3>();
    private List<int> triangles = new List<int>();
    private List<Vector2> uvs = new List<Vector2>();

    public Chunk(Vector2 chunkPos, byte[,,] blocks) {
        this.chunkPos = chunkPos;
        this.blocks = blocks;
        RefreshMeshData();
    }

    public void AddToWorld(World world) {
        long t = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        
        me = new GameObject();
        meshFilter = me.AddComponent<MeshFilter>();
        meshRenderer = me.AddComponent<MeshRenderer>();
        

        meshRenderer.material = world.material;

        me.transform.SetParent(world.transform);
        me.transform.position = new Vector3(chunkPos.x * Data.ChunkSize, 0, chunkPos.y * Data.ChunkSize);

        RefreshMesh();
    }

    private bool IsSolid(Vector3 pos) {

        int x = Mathf.FloorToInt(pos.x);
        int y = Mathf.FloorToInt(pos.y);
        int z = Mathf.FloorToInt(pos.z);

        if (x < 0 || x >= Data.ChunkSize || z < 0 || z >= Data.ChunkSize || y < 0 || y >= Data.ChunkSize) return false;

        return blocks[x, y, z] != 0;
    }

    private void RefreshMeshData() {
        int vertexIndex = 0;
        verts = new List<Vector3>();
        triangles = new List<int>();
        uvs = new List<Vector2>();

        int t = 0;

        for (int y = 0; y < Data.ChunkSize; y++) {
            for (int x = 0; x < Data.ChunkSize; x++) {
                for (int z = 0; z < Data.ChunkSize; z++) {
                    Vector3 delta = new Vector3(x, y, z);
                    for (int i = 0; i < 6; i++) {

                        Vector3 pos = new Vector3(x, y, z);

                        

                        if (blocks[x, y, z] == 0 || IsSolid(pos + Data.faceChecks[i])) continue;

                        if (y == Data.ChunkSize - 1 && i == 2) {
                            t += 1;
                        }

                        verts.Add(pos + Data.vertices[Data.triangles[i, 0]]);
                        verts.Add(pos + Data.vertices[Data.triangles[i, 1]]);
                        verts.Add(pos + Data.vertices[Data.triangles[i, 2]]);
                        verts.Add(pos + Data.vertices[Data.triangles[i, 3]]);

                        Vector2 coord = Data.textureCoords[blocks[x, y, z] - 1, i];
                        uvs.Add(coord);
                        uvs.Add(coord + new Vector2(0f, 0.5f));
                        uvs.Add(coord + new Vector2(0.5f, 0f));
                        uvs.Add(coord + new Vector2(0.5f, 0.5f));

                        triangles.Add(vertexIndex + 0);
                        triangles.Add(vertexIndex + 1);
                        triangles.Add(vertexIndex + 2);
                        triangles.Add(vertexIndex + 2);
                        triangles.Add(vertexIndex + 1);
                        triangles.Add(vertexIndex + 3);

                        vertexIndex += 4;
                    }
                }
            }
        }
    }

    private void RefreshMesh() {
        Mesh mesh = new Mesh();
        mesh.vertices = verts.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.uv = uvs.ToArray();

        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }

    public Vector2 GetPosition() {
        return chunkPos;
    }
}
