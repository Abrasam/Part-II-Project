using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class Data {
    //Class adapted from https://github.com/b3agz/Code-A-Game-Like-Minecraft-In-Unity/blob/master/02-the-first-chunk/Assets/Scripts/VoxelData.cs

    public static readonly int ChunkWidth = 32;
    public static readonly int ChunkHeight = 32;

    public static readonly Vector3[] vertices = new Vector3[8] {
        new Vector3(0.0f, 0.0f, 0.0f),
        new Vector3(1.0f, 0.0f, 0.0f),
        new Vector3(1.0f, 1.0f, 0.0f),
        new Vector3(0.0f, 1.0f, 0.0f),
        new Vector3(0.0f, 0.0f, 1.0f),
        new Vector3(1.0f, 0.0f, 1.0f),
        new Vector3(1.0f, 1.0f, 1.0f),
        new Vector3(0.0f, 1.0f, 1.0f),
    };

    public static readonly int[,] triangles = new int[6, 4] {
        {0, 3, 1, 2},
		{5, 6, 4, 7},
		{3, 7, 2, 6},
		{1, 5, 0, 4},
		{4, 7, 0, 3},
		{1, 2, 5, 6}
	};

    public static readonly Vector3[] faceChecks = new Vector3[6] {

        new Vector3(0.0f, 0.0f, -1.0f),
        new Vector3(0.0f, 0.0f, 1.0f),
        new Vector3(0.0f, 1.0f, 0.0f),
        new Vector3(0.0f, -1.0f, 0.0f),
        new Vector3(-1.0f, 0.0f, 0.0f),
        new Vector3(1.0f, 0.0f, 0.0f)

    };

    public static readonly Vector2[,] textureCoords = new Vector2[3,6] {
        {
            new Vector2(0.5f,0f),
            new Vector2(0.5f,0f),
            new Vector2(0.5f,0f),
            new Vector2(0.5f,0f),
            new Vector2(0.5f,0f),
            new Vector2(0.5f,0f)
        },
        {
            new Vector2(0f,0f),
            new Vector2(0f,0f),
            new Vector2(0f,0.5f),
            new Vector2(0.5f,0.5f),
            new Vector2(0f,0f),
            new Vector2(0f,0f)
        },
        {
            new Vector2(0.5f,0.5f),
            new Vector2(0.5f,0.5f),
            new Vector2(0.5f,0.5f),
            new Vector2(0.5f,0.5f),
            new Vector2(0.5f,0.5f),
            new Vector2(0.5f,0.5f)
        }
    };
}
