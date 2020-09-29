from TestInfo.TestUtils import *


class Test_Manager:
    def __init__(self, gaze_manager):

        self.tag = np.zeros(2)
        self.pixel = np.zeros(2)
        self.error_mm = 0

        self.gaze_manager = gaze_manager
        self.width = gaze_manager.width_px
        self.height = gaze_manager.height_px
        self.person_name = gaze_manager.user_name
        self.pixel_method = gaze_manager.pixel_method
        self.model_method = gaze_manager.model_method

        self.iteration = 0
        self.test_csv = new_csv_session("OurDB")

    def self_check(self):
        self.gaze_manager.gui.print_pixel(self.gaze_manager.get_cur_pixel_mean())
        # un-comment if you want to wait for mouse-clicks to capture
        # self.gaze_manager.gui.wait_key()

    def not_valid_pixel(self):

        log_error(self.test_csv, "pixel")
        self.gaze_manager.gui.button.config(text="pixel was out of bounds! Click to continue")
        self.gaze_manager.gui.wait_key()
        self.gaze_manager.gui.button.config(text="Click to Capture")
        self.iteration -= 1

    def not_valid_detect(self):
        log_error(self.test_csv, "detect")
        self.gaze_manager.gui.button.config(text="Re-center your face to the camera! Click only when ready")
        self.gaze_manager.gui.wait_key()
        self.gaze_manager.gui.button.config(text="Click to Capture")
        self.iteration -= 1

    def draw_target(self):
        self.tag = [random.randint(0, self.width), random.randint(0, self.height)]
        self.gaze_manager.gui.print_pixel(self.tag)
        # wanted the button to move with the tag, but it's not working atm
        # self.gaze_manager.gui.print_capture_button(self.tag)

    def capture(self):
        self.gaze_manager.gui.wait_key()
        self.pixel = self.gaze_manager.get_cur_pixel_mean()
        return self.pixel

    def collect(self):
        for self.iteration in range(15):
            cur_smp = Sample()
            self.draw_target()
            is_valid_pixel = self.capture()
            if is_valid_pixel is error_in_pixel:
                self.not_valid_pixel()
            elif is_valid_pixel is error_in_detect:
                self.not_valid_detect()
            # all valid
            else:
                cur_smp.set_from_session(self.tag, self.pixel, self.gaze_manager.screen_size,
                                         self.gaze_manager.last_distance, self.person_name,
                                         self.pixel_method, self.model_method)
                cur_smp.compute_error(self.gaze_manager.pixel_per_mm)
                log_sample_csv(cur_smp, self.test_csv)
        self.finish_test()

    def finish_test(self):
        self.test_csv.close()
