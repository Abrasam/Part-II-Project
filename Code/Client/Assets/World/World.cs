using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class World : MonoBehaviour {

    public Material material;

    // Start is called before the first frame update
    void Start() {
        byte[,,] blocks = new byte[Data.ChunkWidth,Data.ChunkHeight,Data.ChunkWidth];
        for (int i = 0; i < Data.ChunkWidth; i++) {
            for (int j = 0; j < Data.ChunkHeight; j++) {
                for (int k = 0; k < Data.ChunkWidth; k++) {
                    if (j == Data.ChunkHeight - 1) {
                        blocks[i, j, k] = 2;
                    } else if (j > Data.ChunkHeight - 5) {
                        blocks[i, j, k] = 3;
                    } else {
                        blocks[i, j, k] = 1;
                    }
                    
                }
            }
        }
        new Chunk(this, new Vector2(0, 0), blocks);
        new Chunk(this, new Vector2(1, 0), blocks);
        new Chunk(this, new Vector2(1, 1), blocks);
    }

    // Update is called once per frame
    void Update() {
        
    }
}
