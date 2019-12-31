using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Controller : MonoBehaviour {

    private float horizontal;
    private float vertical;
    private float mouseHorizontal;
    private float mouseVertical;
    private float rot = 0;
    private const float BASE_SPEED = 4;
    private float sprintModifier = 1;
    private Transform cam;
    private World world;
    private const float halfWidth = 0.5f;

    private bool onGround = false;
    private bool jump = false;

    private Vector3 velocity = new Vector3();

    void Start() {
        cam = GameObject.Find("Main Camera").transform;
        Cursor.lockState = CursorLockMode.Locked;
        world = GameObject.Find("World").GetComponent<World>();
    }

    private void FixedUpdate() {
        float vertSpeed = velocity.y;
        velocity = (transform.forward * vertical + transform.right * horizontal) * sprintModifier * BASE_SPEED;
        velocity += Vector3.up * (vertSpeed - 20f * Time.fixedDeltaTime);

        if (jump) {
            if (onGround) {
                velocity.y = 8;
            }
        }

        Vector3 delta = velocity * Time.fixedDeltaTime;

        delta.y = CalculateVerticalDelta(delta);

        if (WillCollide(Vector3.Scale(new Vector3(1, 1, 0), delta))) {
            delta.Scale(new Vector3(0, 1, 1));
            velocity.Scale(new Vector3(0, 1, 1));
        }
        if (WillCollide(Vector3.Scale(new Vector3(0, 1, 1), delta))) {
            delta.Scale(new Vector3(1, 1, 0));
            velocity.Scale(new Vector3(1, 1, 0));
        }

        transform.position += delta;
    }

    private float CalculateVerticalDelta(Vector3 delta) {
        Vector3 newPos = transform.position + Vector3.Scale(new Vector3(0, 1, 0), delta);
        float x, y, z;
        x = newPos.x;
        y = newPos.y;
        z = newPos.z;
        if (delta.y < 0) {
            if (world.IsSolid(x - halfWidth, y, z - halfWidth)
                || world.IsSolid(x - halfWidth, y, z + halfWidth)
                || world.IsSolid(x + halfWidth, y, z + halfWidth)
                || world.IsSolid(x + halfWidth, y, z - halfWidth)) {
                onGround = true;
                velocity.y = 0;
                return 0;
            }
            else {
                onGround = false;
                return delta.y;
            }
        } else {
            onGround = false;
            if (world.IsSolid(x - halfWidth, y, z - halfWidth)
                || world.IsSolid(x - halfWidth, y + 2, z + halfWidth)
                || world.IsSolid(x + halfWidth, y + 2, z + halfWidth)
                || world.IsSolid(x + halfWidth, y + 2, z - halfWidth)) {
                velocity.y = 0;
                return 0;
            } else {
                return delta.y;
            }
        }
    }

    private bool WillCollide(Vector3 velocity) {
        Vector3 newPos = transform.position + velocity;
        float x, y, z;
        x = newPos.x;
        y = newPos.y;
        z = newPos.z;
        return world.IsSolid(x - halfWidth, y, z - halfWidth)
            || world.IsSolid(x - halfWidth, y, z + halfWidth)
            || world.IsSolid(x + halfWidth, y, z + halfWidth)
            || world.IsSolid(x + halfWidth, y, z - halfWidth)
            || world.IsSolid(x - halfWidth, y + 1, z - halfWidth)
            || world.IsSolid(x - halfWidth, y + 1, z + halfWidth)
            || world.IsSolid(x + halfWidth, y + 1, z + halfWidth)
            || world.IsSolid(x + halfWidth, y + 1, z - halfWidth);
    }

    void Update() {
        horizontal = Input.GetAxis("Horizontal");
        vertical = Input.GetAxis("Vertical");
        mouseHorizontal = Input.GetAxis("Mouse X");
        mouseVertical = Input.GetAxis("Mouse Y");
        rot = Mathf.Max(-90,Mathf.Min(90,rot+mouseVertical));
        if (Input.GetButtonDown("Sprint")) {
            sprintModifier = 2;
        }
        if (Input.GetButtonUp("Sprint")) {
            sprintModifier = 1;
        }
        if (Input.GetButtonDown("Jump")) {
            jump = true;
        }
        if (Input.GetButtonUp("Jump")) {
            jump = false;
        }

        transform.Rotate(Vector3.up * mouseHorizontal);
        if (Mathf.Abs(rot) < 90) {
            cam.Rotate(Vector3.right * -mouseVertical);
        }
    }
}
