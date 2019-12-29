using System.Collections;
using System.Collections.Generic;
using System.Collections.Concurrent;
using UnityEngine;
using System.Threading;

public class World : MonoBehaviour {

    public Material material;
    private float tickTimer = 0;
    private ConcurrentQueue<Update> updates = new ConcurrentQueue<Update>();
    private ConcurrentQueue<Update> events = new ConcurrentQueue<Update>();
    private GameObject player;
    private GameObject player2;
    private List<Chunk> chunks = new List<Chunk>();

    private NetworkThread nt;

    // Start is called before the first frame update
    void Start() {
        byte[,,] blocks = new byte[Data.ChunkSize, Data.ChunkSize, Data.ChunkSize];
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
        player2 = GameObject.Find("player2");
        player = GameObject.Find("Player");
        nt = new NetworkThread(this, updates, events, "127.0.0.1", 25566);
    }

    // Update is called once per frame
    void Update() {
        tickTimer += Time.deltaTime;
        if (tickTimer > Data.TickLength) {
            //Push events to queue.
            events.Enqueue(new Update(UpdateType.PLAYER_MOVE, player.transform.position));
            //Pop packets from queue.
            int cnt = updates.Count;
            for (int i = 0; i < cnt; i++) {
                Update update;
                if (updates.TryDequeue(out update)) {
                    switch(update.type) {
                        case UpdateType.PLAYER_MOVE:
                            player2.transform.position = (Vector3)update.arg;
                            break;
                        case UpdateType.LOAD_CHUNK:
                            Chunk newChunk = (Chunk)update.arg;
                            newChunk.AddToWorld(this);
                            chunks.Add(newChunk);
                            break;
                        case UpdateType.UNLOAD_CHUNK:
                            Vector2 pos = (Vector2)update.arg;
                            List<Chunk> rem = new List<Chunk>();
                            foreach (Chunk c in chunks) {
                                if (c.GetPosition().Equals(pos)) {
                                    Destroy(c.me);
                                    rem.Add(c);
                                    break;
                                }
                            }
                            foreach(Chunk r in rem) {
                                chunks.Remove(r);
                            }
                            break;
                        default:
                            Debug.Log("Invalid update type received?");
                            break;
                    }
                }
            }
        }
    }

    void OnApplicationQuit() {
        nt.Abort();
    }
}

public class Update {
    public readonly UpdateType type;
    public readonly object arg;

    public Update(UpdateType type, object arg) {
        this.type = type;
        this.arg = arg;
    }
}

public enum UpdateType {
    PLAYER_MOVE = 1,
    LOAD_CHUNK = 2,
    UNLOAD_CHUNK = 3
}
