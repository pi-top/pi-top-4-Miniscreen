from time import sleep

from pitop import Camera, DriveController, Pitop
from pitop.processing.algorithms.line_detect import process_frame_for_line

# Assemble a robot
robot = Pitop()
robot.miniscreen.display_multiline_text("Connect motors to M0 and M3 and a Camera")
sleep(3)
robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(Camera())


# Set up logic based on line detection
def drive_based_on_frame(frame):
    processed_frame = process_frame_for_line(frame)

    if processed_frame.line_center is None:
        print("Line is lost!", end="\r")
        robot.drive.stop()
    else:
        print(f"Target angle: {processed_frame.angle:.2f} deg ", end="\r")
        robot.drive.forward(0.25, hold=True)
        robot.drive.target_lock_drive_angle(processed_frame.angle)
        robot.miniscreen.display_image(processed_frame.robot_view)


robot.miniscreen.display_multiline_text("Press any button to exit")
sleep(3)

# On each camera frame, detect a line
robot.camera.on_frame = drive_based_on_frame

# Handle exit condition
button_pressed = False


def toggle_button_pressed():
    global button_pressed
    button_pressed = not button_pressed


robot.miniscreen.up_button.when_pressed = toggle_button_pressed
robot.miniscreen.down_button.when_pressed = toggle_button_pressed
robot.miniscreen.select_button.when_pressed = toggle_button_pressed
robot.miniscreen.cancel_button.when_pressed = toggle_button_pressed

# Run!
while not button_pressed:
    sleep(1)

robot.drive.stop()
