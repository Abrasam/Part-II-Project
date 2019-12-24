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

public class SocketThread {

    private readonly string address;
    private readonly int port;
    private readonly int[] chunkCoord;

    private Socket socket;
    private Thread recvThread;
    private Thread sendThread;

    public readonly BlockingCollection<Packet> recv;
    private readonly BlockingCollection<Packet> send;
    
    public SocketThread(string address, int port, int chunkX, int chunkY) {
        this.address = address;
        this.port = port;
        this.chunkCoord = new int[2] {chunkX, chunkY};
        recv = new BlockingCollection<Packet>(new ConcurrentQueue<Packet>());
        send = new BlockingCollection<Packet>(new ConcurrentQueue<Packet>());

        IPEndPoint ipe = new IPEndPoint(IPAddress.Parse(address), port);

        socket = new Socket(ipe.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        socket.ReceiveTimeout = 1000;

        socket.Connect(ipe);

        socket.Send(System.Text.Encoding.UTF8.GetBytes("{\"type\": \"connect\", \"chunk\": [" + chunkCoord[0] + "," + chunkCoord[1] + "]}"));

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
        while (true) {
            byte[] buf = new byte[1];
            List<byte> msg = new List<byte>();
            socket.Receive(buf);
            while (buf[0] != (byte)'\n') {
                msg.Add(buf[0]);
                socket.Receive(buf);
            }
            byte[] data = msg.ToArray();
            recv.Add(JsonUtility.FromJson<Packet>(System.Text.Encoding.UTF8.GetString(data)));
        }
    }

    private void SendLoop() {
        while (true) {
            Packet p = send.Take();
            Debug.Log("Packet outgoing!");
            string json = JsonUtility.ToJson(p) + "\n";
            byte[] toSend = System.Text.Encoding.UTF8.GetBytes(json);
            socket.Send(toSend);
        }
    }

    public void Send(Packet p) {
        send.Add(p);
    }
}

public class NetworkThread {

    private World world;
    private ConcurrentQueue<Update> updates;
    private List<SocketThread> clients = new List<SocketThread>();
    private Thread thread;

    public NetworkThread(World world, ConcurrentQueue<Update> updates) {
        this.world = world;
        this.updates = updates;
        for (int i = -1; i < 2; i++) {
            for (int j = -1; j < 2; j++) {
                try {
                SocketThread st = new SocketThread("127.0.0.1", 25566, i, j);
                st.Send(new Packet((int)PacketType.PLAYER_REGISTER, new int[0]));
                clients.Add(st);
                } catch (ServerRejectedException e) {
                    Debug.Log("Chunk not on this server.");
                }
            }
        }
        thread = new Thread(Run);
        thread.IsBackground = true;
        thread.Start();
    }

    private void Run() {
        while (true) {
            foreach (SocketThread s in clients) {
                int cnt = s.recv.Count;
                for (int i = 0; i < cnt; i++) {
                    Packet p = s.recv.Take();
                    Debug.Log("Received packet");
                    switch (p.type) {
                        case (int)PacketType.CHUNK_DATA:
                            byte[,,] chunkData = new byte[Data.ChunkSize, Data.ChunkSize, Data.ChunkSize];
                            for (int x = 0; x < Data.ChunkSize; x++) {
                                for (int y = 0; y < Data.ChunkSize; y++) {
                                    for (int z = 0; z < Data.ChunkSize; z++) {
                                        chunkData[x, y, z] = (byte)p.args[2 + 32 * 32 * x + 32 * y + z];
                                    }
                                }
                            }
                            updates.Enqueue(new Update(UpdateType.CHUNK_DATA, new Chunk(new Vector2(p.args[0], p.args[1]), chunkData)));
                            break;
                        default:
                            break;
                    }
                }
            }
            Thread.Sleep((int)(Data.TickLength * 1000));
        }
    }
}

[Serializable]
public class Packet {
    public int type;
    public int[] args;
    
    public Packet(int type, int[] args) {
        this.type = type;
        this.args = args;
    }
}

public enum PacketType {
    FIND_CHUNK = 0,
    PLAYER_REGISTER = 1,
    PLAYER_DEREGISTER = 2,
    PLAYER_MOVE = 2,
    FIND_PLAYER = 4,
    CHUNK_DATA = 5
}