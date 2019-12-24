using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Movement : MonoBehaviour {

    private float horizontal;
    private float vertical;
    private float mouseHorizontal;
    private float mouseVertical;
    private const float SPEED = 10;
    private float mod = 1;
    private Transform cam;

    // Start is called before the first frame update
    void Start() {
        cam = GameObject.Find("Main Camera").transform;
    }

    // Update is called once per frame
    void Update() {
        horizontal = Input.GetAxis("Horizontal");
        vertical = Input.GetAxis("Vertical");
        mouseHorizontal = Input.GetAxis("Mouse X");
        mouseVertical = Input.GetAxis("Mouse Y");

        if (Input.GetButtonDown("Sprint")) {
            mod = 10;
        }
        if (Input.GetButtonUp("Sprint")) {
            mod = 1;
        }

        transform.Rotate(Vector3.up * mouseHorizontal);
        cam.Rotate(Vector3.right * -mouseVertical);
        transform.Translate(cam.forward.normalized * vertical * Time.deltaTime * SPEED * mod, Space.World);
        transform.Translate(cam.right.normalized * horizontal * Time.deltaTime * SPEED * mod, Space.World);
    }
}
