﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class Constants {

    public static readonly int ChunkSize = 32;
    public static readonly float TickLength = 1 / 20;

    public static readonly Vector3[] vertices = new Vector3[8] {
        new Vector3(-0.001f, -0.001f, -0.001f),
        new Vector3(1.001f, -0.001f, -0.001f),
        new Vector3(1.001f, 1.001f, -0.001f),
        new Vector3(-0.001f, 1.001f, -0.001f),
        new Vector3(-0.001f, -0.001f, 1.001f),
        new Vector3(1.001f, -0.001f, 1.001f),
        new Vector3(1.001f, 1.001f, 1.001f),
        new Vector3(-0.001f, 1.001f, 1.001f),
    };

    public static readonly int[,] triangles = new int[6, 4] {
        {0, 3, 1, 2},
		{5, 6, 4, 7},
		{3, 7, 2, 6},
		{1, 5, 0, 4},
		{4, 7, 0, 3},
		{1, 2, 5, 6}
	};

    public static readonly Vector3[] faceNormals = new Vector3[6] {

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
