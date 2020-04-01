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
    private string username;
    private Dictionary<Vector2, Chunk> chunks = new Dictionary<Vector2, Chunk>();

    private NetworkThread nt;

    private GameObject sun;

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
        player = GameObject.Find("Player");
        sun = GameObject.Find("Sun");

        byte[] bytes = new byte[10];

        new System.Random().NextBytes(bytes);

        username = "Abrasam";// string.Join("",bytes);

        nt = new NetworkThread(this, username, updates, events, "5.135.160.191", 24001); //5.135.160.191 28015
        player.transform.position = nt.GetLocation();
        nt.Start();
    }

    // Update is called once per frame
    void Update() {
        tickTimer += Time.deltaTime;
        if (tickTimer > Data.TickLength) {
            //Push events to queue.
            events.Enqueue(new Update(UpdateType.PLAYER_MOVE, username, new float[] { player.transform.position.x, player.transform.position.y, player.transform.position.z, player.transform.eulerAngles.y }));
            //Pop packets from queue.
            int cnt = updates.Count;
            for (int i = 0; i < cnt; i++) {
                Update update;
                if (updates.TryDequeue(out update)) {
                    switch (update.type) {
                        case UpdateType.PLAYER_ADD:
                            Chunk chunk;
                            if (chunks.TryGetValue((Vector2)update.arg, out chunk)) {
                                GameObject deleteMe = chunk.GetAndRemovePlayer(update.player);
                                if (deleteMe != null) Destroy(deleteMe);
                                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                                go.transform.localScale = new Vector3(0.6f, 1.8f, 0.6f);
                                chunk.AddPlayer(update.player, go);
                            }
                            break;
                        case UpdateType.PLAYER_REMOVE:
                            Chunk chunk2;
                            if (chunks.TryGetValue((Vector2)update.arg, out chunk2)) {
                                GameObject go = chunk2.GetAndRemovePlayer(update.player);
                                if (go != null) Destroy(go);
                            }
                            break;
                        case UpdateType.PLAYER_MOVE:
                            Chunk chunk3;
                            float[] arg = (float[])update.arg;
                            Vector3 pos = new Vector3(arg[0], arg[1], arg[2]);
                            if (chunks.TryGetValue(new Vector2(Mathf.FloorToInt(pos.x / Data.ChunkSize), Mathf.FloorToInt(pos.z / Data.ChunkSize)), out chunk3)) {
                                GameObject moved = chunk3.GetPlayer(update.player);
                                if (moved != null) {
                                    moved.transform.position = pos + Vector3.up;
                                    moved.transform.eulerAngles = new Vector3(transform.eulerAngles.x, arg[3], transform.eulerAngles.z);
                                }
                            }
                            break;
                        case UpdateType.LOAD_CHUNK:
                            Chunk newChunk = (Chunk)update.arg;
                            Vector3 newPos = newChunk.GetPosition();
                            Chunk oldChunk;
                            newChunk.AddToWorld(this);
                            if (chunks.TryGetValue(newPos, out oldChunk)) {
                                foreach (string name in oldChunk.GetAllPlayerNames()) {
                                    newChunk.AddPlayer(name, oldChunk.GetPlayer(name));
                                }
                                Destroy(oldChunk.me);
                                chunks.Remove(newPos);
                            }
                            chunks.Add(newPos, newChunk);
                            break;
                        case UpdateType.UNLOAD_CHUNK:
                            Vector2 chunkPos = (Vector2)update.arg;
                            Chunk rem;
                            if (chunks.TryGetValue(chunkPos, out rem)) {
                                chunks.Remove(chunkPos);
                                Destroy(rem.me);
                                foreach (GameObject player in rem.GetAllPlayers()) {
                                    Destroy(player);
                                }
                            }
                            break;
                        case UpdateType.TIME:
                            sun.transform.eulerAngles = new Vector3((float)update.arg * 360 - 90, 0, 0);
                            float time = (float)update.arg;
                            float intensity = 1;
                            if (time < 3 * 60 / 1440f || time > 21 * 60 / 1440f) {
                                intensity = 0;
                            }
                            else if (time < 6 * 60 / 1440f) {
                                intensity = 8 * time - 1;
                            }
                            else if (time > 18 * 60 / 1440f) {
                                intensity = 7 - 8 * time;
                            }
                            sun.GetComponent<Light>().intensity = 1.4f * intensity;
                            break;
                        default:
                            break;
                    }
                }
            }
        }
    }

    public bool IsSolid(float x, float y, float z) {

        int xi = Mathf.FloorToInt(x);
        int yi = Mathf.FloorToInt(y);
        int zi = Mathf.FloorToInt(z);

        int chunkX = Mathf.FloorToInt(xi / (float)Data.ChunkSize);
        int chunkY = Mathf.FloorToInt(zi / (float)Data.ChunkSize);

        xi -= (chunkX * Data.ChunkSize);
        zi -= (chunkY * Data.ChunkSize);

        Chunk chunk;
        if (chunks.TryGetValue(new Vector2(chunkX, chunkY), out chunk)) {
            return chunk.IsSolid(new Vector3(xi, yi, zi));
        }
        return true; //If not loaded assume solid for safety.
    }

    public void DestroyBlock(Vector3 pos) {
        events.Enqueue(new Update(UpdateType.BLOCK_CHANGE, username, new float[] { pos.x, pos.y, pos.z, 0 }));
    }

    public void PlaceBlock(Vector3 pos, int type) {
        events.Enqueue(new Update(UpdateType.BLOCK_CHANGE, username, new float[] { pos.x, pos.y, pos.z, type }));
    }


    void OnApplicationQuit() {
        nt.Abort();
    }
}

public class Update {
    public readonly UpdateType type;
    public readonly string player;
    public readonly object arg;

    public Update(UpdateType type, string player, object arg) {
        this.type = type;
        this.player = player;
        this.arg = arg;
    }
}

public enum UpdateType {
    PLAYER_MOVE = 1,
    LOAD_CHUNK = 2,
    UNLOAD_CHUNK = 3,
    PLAYER_ADD = 4,
    PLAYER_REMOVE = 5,
    TIME = 6,
    BLOCK_CHANGE = 7,
}
