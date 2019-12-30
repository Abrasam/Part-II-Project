﻿using System.Collections;
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
    private string name;
    private Dictionary<Vector2, Chunk> chunks = new Dictionary<Vector2, Chunk>();

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
        player = GameObject.Find("Player");

        byte[] bytes = new byte[10];

        new System.Random().NextBytes(bytes);

        name = string.Join("",bytes);

        nt = new NetworkThread(this, name, updates, events, "127.0.0.1", 25566);
    }

    // Update is called once per frame
    void Update() {
        tickTimer += Time.deltaTime;
        if (tickTimer > Data.TickLength) {
            //Push events to queue.
            events.Enqueue(new Update(UpdateType.PLAYER_MOVE, name, player.transform.position));
            //Pop packets from queue.
            int cnt = updates.Count;
            for (int i = 0; i < cnt; i++) {
                Update update;
                if (updates.TryDequeue(out update)) {
                    switch(update.type) {
                        case UpdateType.PLAYER_ADD:
                            Chunk chunk;
                            if (chunks.TryGetValue((Vector2)update.arg, out chunk)) {
                                Debug.Log("Found chunk.");
                                GameObject deleteMe = chunk.GetAndRemovePlayer(update.player);
                                if (deleteMe != null) Destroy(deleteMe);
                                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
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
                            Vector3 pos = (Vector3)update.arg;
                            if (chunks.TryGetValue(new Vector2(Mathf.FloorToInt(pos.x / Data.ChunkSize), Mathf.FloorToInt(pos.z / Data.ChunkSize)), out chunk3)) {
                                GameObject moved = chunk3.GetPlayer(update.player);
                                if (moved != null) moved.transform.position = pos;
                            }
                            break;
                        case UpdateType.LOAD_CHUNK:
                            Chunk newChunk = (Chunk)update.arg;
                            newChunk.AddToWorld(this);
                            chunks.Add(newChunk.GetPosition(), newChunk);
                            break;
                        case UpdateType.UNLOAD_CHUNK:
                            Vector2 chunkPos = (Vector2)update.arg;
                            Chunk rem;
                            if (chunks.TryGetValue(chunkPos, out rem)) {
                                chunks.Remove(chunkPos);
                                Destroy(rem.me);
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


    //Adapted from https://github.com/b3agz/Code-A-Game-Like-Minecraft-In-Unity/blob/49e95cecaffc25e86a7aa4402e2c9848a863d8a6/06-character-controller/Assets/Scripts/World.cs#L106
    public bool IsSolid(float x, float y, float z) {

        int xCheck = Mathf.FloorToInt(x);
        int yCheck = Mathf.FloorToInt(y);
        int zCheck = Mathf.FloorToInt(z);

        int xChunk = Mathf.FloorToInt(xCheck / (float)Data.ChunkSize);
        int zChunk = Mathf.FloorToInt(zCheck / (float)Data.ChunkSize);

        xCheck -= (xChunk * Data.ChunkSize);
        zCheck -= (zChunk * Data.ChunkSize);


        Chunk chunk;
        if (chunks.TryGetValue(new Vector2(xChunk, zChunk), out chunk)) {
            return chunk.IsSolid(new Vector3(xCheck, yCheck, zCheck));
        }
        return true; //If not loaded assume solid for safety.
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
    PLAYER_REMOVE = 5
}
