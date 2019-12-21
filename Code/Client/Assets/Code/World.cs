using System.Collections;
using System.Collections.Generic;
using System.Collections.Concurrent;
using UnityEngine;

public class World : MonoBehaviour {

    public Material material;
    private float tickTimer = 0;
    private ConcurrentQueue<Update> updateQueue = new ConcurrentQueue<Update>();

    // Start is called before the first frame update
    void Start() {
        byte[,,] blocks = new byte[Data.ChunkSize,Data.ChunkSize, Data.ChunkSize];
        for (int i = 0; i < Data.ChunkSize; i++) {
            for (int j = 0; j < Data.ChunkSize; j++) {
                for (int k = 0; k < Data.ChunkSize; k++) {
                    if (j == Data.ChunkSize - 1) {
                        blocks[i, j, k] = 2;
                    } else if (j > Data.ChunkSize - 5) {
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
        tickTimer += Time.deltaTime;
        if (tickTimer > Data.TickLength) {
            //Push events to queue.
        }
    }
}

class Update {
    private UpdateType type;

    public Update(UpdateType type) {
        this.type = type;
    }
}

enum UpdateType {
    PLAYER_MOVE = 1
}
