using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Collections.Concurrent;
using System;

public class SocketThread {

    private readonly string address;
    private readonly int port;

    private Socket socket;
    private Thread recvThread;
    private Thread sendThread;
    private BlockingCollection<Packet> recv;
    private BlockingCollection<Packet> send;

    public SocketThread(string address, int port) {
        this.address = address;
        this.port = port;

        IPEndPoint ipe = new IPEndPoint(Dns.GetHostEntry(address).AddressList[0], port);

        this.socket = new Socket(ipe.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        socket.Connect(ipe);
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
            byte type = data[0];
            byte[] args = new byte[data.Length - 1];
            Array.Copy(data, args, 1);
            recv.Add(JsonUtility.FromJson<Packet>(System.Text.Encoding.UTF8.GetString(args)));
        }
    }

    private void SendLoop() {
        while (true) {
            Packet p = send.Take();
            string json = JsonUtility.ToJson(p);
            byte[] toSend = System.Text.Encoding.UTF8.GetBytes(json);
            socket.Send(toSend);
        }
    }

    public void Send(Packet p) {
        send.Add(p);
    }

    public void Abort() {
        recvThread.Abort();
        sendThread.Abort();
        socket.Shutdown(SocketShutdown.Both);
        socket.Close();
    }
}

[Serializable]
public class Packet {
    public readonly int type;
    public readonly List<int> args;
    
    public Packet(int type, List<int> args) {
        this.type = type;
        this.args = args;
    }
}
