using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WireFrame : MonoBehaviour {

    private World world;
    private Vector3 destroy;
    private Vector3 place;
    private bool valid = true;
    private const float step = 0.5f;
    private const float reach = 5;

    void Start() {
        world = GameObject.Find("World").GetComponent<World>();
    }

    int blockType = 1;

    void Update() {
        float dist = 0;
        while (dist < reach) {
            place = new Vector3(destroy.x, destroy.y, destroy.z);
            dist += step;
            destroy = transform.position + transform.forward * dist;
            destroy = new Vector3(Mathf.FloorToInt(destroy.x), Mathf.FloorToInt(destroy.y), Mathf.FloorToInt(destroy.z));
            if (world.IsSolid(destroy.x, destroy.y, destroy.z)) break;
        }
        valid = world.IsSolid(destroy.x, destroy.y, destroy.z);

        if (Input.GetButtonDown("Left")) {
            if (valid) {
                world.DestroyBlock(destroy);
            }
        }
        if (Input.GetButtonDown("Right")) {
            if (valid) {
                world.PlaceBlock(place, blockType);
            }
        }
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (scroll < 0) {
            blockType = blockType - 1;
            if (blockType <= 0) blockType = 3;
        } else if (scroll > 0) {
            blockType = blockType + 1;
            if (blockType > 3) {
                blockType = 1;
            }
        }
    }

    private void OnPostRender() {
        if (!valid) return;
        GL.Begin(GL.LINES);
        GL.Color(Color.white);
        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z - 0.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z - 0.02f);

        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z - 0.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y + 1.02f, destroy.z - 0.02f);

        GL.Vertex3(destroy.x - 0.02f, destroy.y - 0.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y - 0.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y + 1.02f, destroy.z - 0.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y + 1.02f, destroy.z - 0.02f);
        GL.Vertex3(destroy.x + 1.02f, destroy.y + 1.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x + 1.02f, destroy.y + 1.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z + 1.02f);

        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z + 1.02f);
        GL.Vertex3(destroy.x - 0.02f, destroy.y + 1.02f, destroy.z - 0.02f);
        GL.End();
    }
}
