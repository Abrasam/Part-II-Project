using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Chunk {

    public GameObject me;
    public MeshRenderer meshRenderer;
    public MeshFilter meshFilter;

    private Vector2 chunkPos;
    private byte[,,] blocks;

    public Chunk(World world, Vector2 chunkPos, byte[,,] blocks) {
        this.chunkPos = chunkPos;
        this.blocks = blocks;

        me = new GameObject();
        meshFilter = me.AddComponent<MeshFilter>();
        meshRenderer = me.AddComponent<MeshRenderer>();

        meshRenderer.material = world.material;

        me.transform.SetParent(world.transform);
        me.transform.position = new Vector3(chunkPos.x * Data.ChunkWidth, 0, chunkPos.y * Data.ChunkWidth);

        RefreshMesh();
    }

    private bool IsSolid(Vector3 pos) {

        int x = Mathf.FloorToInt(pos.x);
        int y = Mathf.FloorToInt(pos.y);
        int z = Mathf.FloorToInt(pos.z);

        if (x < 0 || x >= Data.ChunkWidth || z < 0 || z >= Data.ChunkWidth || y < 0 || y >= Data.ChunkHeight) return false;

        return blocks[x, y, z] != 0;
    }

    void RefreshMesh() {
        int vertexIndex = 0;
        List<Vector3> verts = new List<Vector3>();
        List<int> triangles = new List<int>();
        List<Vector2> uvs = new List<Vector2>();

        int t = 0;

        for (int y = 0; y < Data.ChunkHeight; y++) {
            for (int x = 0; x < Data.ChunkWidth; x++) {
                for (int z = 0; z < Data.ChunkWidth; z++) {
                    Vector3 delta = new Vector3(x, y, z);
                    for (int i = 0; i < 6; i++) {

                        Vector3 pos = new Vector3(x, y, z);

                        

                        if (blocks[x, y, z] == 0 || IsSolid(pos + Data.faceChecks[i])) continue;

                        if (y == Data.ChunkHeight - 1 && i == 2) {
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

        Debug.Log(t);

        Mesh mesh = new Mesh();
        mesh.vertices = verts.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.uv = uvs.ToArray();

        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }
}
