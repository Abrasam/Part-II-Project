using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Collections.Concurrent;
using System;

public class ServerRejectedException : Exception {
    public ServerRejectedException(string msg) : base(msg) {}
}

public class ChunkThread {

    private readonly string address;
    private readonly int port;
    private readonly int[] chunkCoord;

    private Socket socket;
    private Thread recvThread;
    private Thread sendThread;

    public readonly BlockingCollection<Packet> recv;
    private readonly BlockingCollection<Packet> send;
    
    public ChunkThread(string address, int port, string player, int chunkX, int chunkY) {
        this.address = address;
        this.port = port;
        this.chunkCoord = new int[2] {chunkX, chunkY};
        recv = new BlockingCollection<Packet>(new ConcurrentQueue<Packet>());
        send = new BlockingCollection<Packet>(new ConcurrentQueue<Packet>());

        IPEndPoint ipe = new IPEndPoint(IPAddress.Parse(address), port);

        socket = new Socket(ipe.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        socket.ReceiveTimeout = 1000;

        socket.Connect(ipe);

        socket.Send(System.Text.Encoding.UTF8.GetBytes("{\"type\": \"connect\", \"chunk\": [" + chunkCoord[0] + "," + chunkCoord[1] + "], \"player\":\"" + player + "\"}"));

        byte[] ok = new byte[2];

        socket.Receive(ok);

        socket.ReceiveTimeout = 0;

        if (System.Text.Encoding.UTF8.GetString(ok) != "ok") {
            throw new ServerRejectedException("Server did not accept connection.");
        }

        recvThread = new Thread(RecvLoop);
        recvThread.IsBackground = true;
        recvThread.Start();
        sendThread = new Thread(SendLoop);
        sendThread.IsBackground = true;
        sendThread.Start();
    }

    private void RecvLoop() {
        try {
            byte newLine = System.Text.Encoding.UTF8.GetBytes("\n")[0];
            while (true) {
                byte[] buf = new byte[1];
                List<byte> msg = new List<byte>();
                socket.Receive(buf);
                while (buf[0] != newLine) {
                    msg.Add(buf[0]);
                    socket.Receive(buf);
                }
                byte[] data = msg.ToArray();
                recv.Add(JsonUtility.FromJson<Packet>(System.Text.Encoding.UTF8.GetString(data)));
            }
        } catch (SocketException) {
            return;
        } catch (ObjectDisposedException) {
            return;
        }
    }

    private void SendLoop() {
        try {
            while (true) {
                Packet p = send.Take();
                string json = JsonUtility.ToJson(p) + "\n";
                byte[] toSend = System.Text.Encoding.UTF8.GetBytes(json);
                socket.Send(toSend);
            }
        } catch (SocketException) {
            return;
        } catch (ObjectDisposedException) {
            return;
        }
    }

    public void Send(Packet p) {
        send.Add(p);
    }

    public Vector2 GetChunkCoord() {
        return new Vector2(chunkCoord[0], chunkCoord[1]);
    }

    public bool IsAlive() {
        return sendThread.IsAlive && recvThread.IsAlive;
    }

    public void Abort() {
        socket.Close();
    }
}

public class NetworkThread {

    private World world;
    private ConcurrentQueue<Update> incomingUpdates;
    private ConcurrentQueue<Update> outgoingUpdates;
    private string bootstrapAddress;
    private int bootstrapPort;
    private Socket socket;
    private List<ChunkThread> servers = new List<ChunkThread>();
    private string player;

    private Thread eventThread;
    private ChunkThread current;

    public NetworkThread(World world, string player, ConcurrentQueue<Update> incoming, ConcurrentQueue<Update> outgoing, string bootstrapAddress, int bootstrapPort) {
        this.world = world;
        this.incomingUpdates = incoming;
        this.outgoingUpdates = outgoing;
        this.bootstrapAddress = bootstrapAddress;
        this.bootstrapPort = bootstrapPort;
        this.player = player;

        IPEndPoint ipe = new IPEndPoint(IPAddress.Parse(bootstrapAddress), bootstrapPort);

        socket = new Socket(ipe.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        socket.ReceiveTimeout = 1000;

        socket.Connect(ipe);

        socket.Send(System.Text.Encoding.UTF8.GetBytes("{\"type\": \"dht\"}"));
        Debug.Log(System.Text.Encoding.UTF8.GetBytes("{\"type\": \"dht\"}")[0]);

        byte[] ok = new byte[2];

        socket.Receive(ok);

        socket.ReceiveTimeout = 0;

        if (System.Text.Encoding.UTF8.GetString(ok) != "ok") {
            throw new ServerRejectedException("Server did not accept connection.");
        }
    }

    public void Start() {
        if (eventThread == null) {
            eventThread = new Thread(EventHandler);
            eventThread.IsBackground = true;
            eventThread.Start();
        }
    }
    
    public Vector3 GetLocation() {
        socket.Send(System.Text.Encoding.UTF8.GetBytes("\x1{\"name\": \"" + player + "\"}"));
        List<byte> loc = new List<byte>();
        byte[] buf = new byte[1024];
        int n = socket.Receive(buf);
        for (int i = 0; i < n; i++) {
            loc.Add(buf[i]);
        }
        Debug.Log(System.Text.Encoding.UTF8.GetString(loc.ToArray()));
        return JsonUtility.FromJson<Vector3>(System.Text.Encoding.UTF8.GetString(loc.ToArray()));
    }

    private void UpdateChunks(Vector3 pos) {
        int chunkX = Mathf.FloorToInt(pos.x / Constants.ChunkSize);
        int chunkY = Mathf.FloorToInt(pos.z / Constants.ChunkSize);
        List<ChunkThread> rem = new List<ChunkThread>();
        foreach (ChunkThread ct in servers) {
            Vector2 chunk = ct.GetChunkCoord();
            if (!(Math.Abs(chunk.x - chunkX) < 5 && Math.Abs(chunk.y - chunkY) < 5) || !ct.IsAlive()) {
                rem.Add(ct);
            }
        }
        foreach (ChunkThread r in rem) {
            servers.Remove(r);
            r.Abort();
            incomingUpdates.Enqueue(new Update(UpdateType.UNLOAD_CHUNK, "", r.GetChunkCoord()));
        }
        Debug.Log(servers.Count);
        for (int i = -1; i < 2; i++) {
            for (int j = -1; j < 2; j++) {
                bool found = false;
                foreach (ChunkThread ct in servers) {
                    Vector2 chunk = ct.GetChunkCoord();
                    if (chunkX + i == chunk.x && chunkY + j == chunk.y) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    socket.Send(System.Text.Encoding.UTF8.GetBytes("\x0[" + (chunkX + i) + "," + (chunkY + j) + "]"));
                    byte[] buf = new byte[1];
                    List<byte> msg = new List<byte>();
                    socket.Receive(buf);
                    while (buf[0] != (byte)'\n') {
                        msg.Add(buf[0]);
                        socket.Receive(buf);
                    }
                    byte[] data = msg.ToArray();
                    Address addr = JsonUtility.FromJson<Address>(System.Text.Encoding.UTF8.GetString(data));
                    ChunkThread ct = new ChunkThread(addr.ip, addr.port, player, chunkX + i, chunkY + j);
                    servers.Add(ct);
                }
            }
        }
        if (current == null || !current.GetChunkCoord().Equals(new Vector2(chunkX, chunkY))) {
            foreach (ChunkThread ct in servers) {
                if (ct.GetChunkCoord().Equals(new Vector2(chunkX, chunkY))) {
                    if (current != null) {
                        Vector2 coord = current.GetChunkCoord();
                        current.Send(new Packet((int)PacketType.PLAYER_DEREGISTER, new float[] {coord.x, coord.y}, player));
                    }
                    current = ct;
                    current.Send(new Packet((int)PacketType.PLAYER_REGISTER, new float[] {Mathf.FloorToInt(pos.x/Constants.ChunkSize), Mathf.FloorToInt(pos.z/Constants.ChunkSize)}, player));
                    break;
                }
            }
        }
    }

    private void EventHandler() {
        while (true) {
            int localUpdates = outgoingUpdates.Count;
            for (int i = 0; i < localUpdates; i++) {
                Update u;
                if (outgoingUpdates.TryDequeue(out u)) {
                    switch (u.type) {
                        case UpdateType.PLAYER_MOVE:
                            float[] arg = (float[])u.arg;
                            UpdateChunks(new Vector3(arg[0], arg[1], arg[2]));
                            current.Send(new Packet((int)PacketType.PLAYER_MOVE, arg, player));
                            break;
                        case UpdateType.BLOCK_CHANGE:
                            foreach (ChunkThread ct in servers) {
                                ct.Send(new Packet((int)PacketType.BLOCK_CHANGE, (float[])u.arg, u.player));
                            }
                            break;
                        default:
                            break;
                    }
                }
            }
            foreach (ChunkThread s in servers) {
                int cnt = s.recv.Count;
                for (int i = 0; i < cnt; i++) {
                    Packet p = s.recv.Take();
                    switch (p.type) {
                        case (int)PacketType.CHUNK_DATA:
                            byte[,,] chunkData = new byte[Constants.ChunkSize, Constants.ChunkSize, Constants.ChunkSize];
                            for (int x = 0; x < Constants.ChunkSize; x++) {
                                for (int y = 0; y < Constants.ChunkSize; y++) {
                                    for (int z = 0; z < Constants.ChunkSize; z++) {
                                        chunkData[x, y, z] = (byte)p.args[2 + Constants.ChunkSize * Constants.ChunkSize * x + Constants.ChunkSize * y + z];
                                    }
                                }
                            }
                            incomingUpdates.Enqueue(new Update(UpdateType.LOAD_CHUNK, "", new Chunk(new Vector2(p.args[0], p.args[1]), chunkData)));
                            break;
                        case (int)PacketType.PLAYER_MOVE:
                            incomingUpdates.Enqueue(new Update(UpdateType.PLAYER_MOVE, p.player, p.args));
                            break;
                        case (int)PacketType.PLAYER_REGISTER:
                            incomingUpdates.Enqueue(new Update(UpdateType.PLAYER_ADD, p.player, new Vector2(p.args[0], p.args[1])));
                            break;
                        case (int)PacketType.PLAYER_DEREGISTER:
                            incomingUpdates.Enqueue(new Update(UpdateType.PLAYER_REMOVE, p.player, new Vector2(p.args[0], p.args[1])));
                            break;
                        case (int)PacketType.TIME:
                            incomingUpdates.Enqueue(new Update(UpdateType.TIME, "", p.args[0] / 1440));
                            break;
                        default:
                            break;
                    }
                }
            }
            Thread.Sleep((int)(Constants.TickLength * 1000));
        }
    }

    public void Abort() {
        eventThread.Abort();
        foreach (ChunkThread ct in servers) {
            ct.Abort();
        }
    }

    [Serializable]
    private class Address {
        public string ip;
        public int port;
    }
}

[Serializable]
public class Packet {
    public int type;
    public float[] args;
    public string player;
    
    public Packet(int type, float[] args, string player) {
        this.type = type;
        this.args = args;
        this.player = player;
    }
}

public enum PacketType {
    FIND_CHUNK = 0,
    PLAYER_REGISTER = 1,
    PLAYER_DEREGISTER = 2,
    PLAYER_MOVE = 3,
    FIND_PLAYER = 4,
    CHUNK_DATA = 5,
    TIME = 6,
    BLOCK_CHANGE = 7,
}