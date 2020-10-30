import UtilsAndModels.utils as utils
from UtilsAndModels.Defines import *


class FrameData:
    def __init__(self, img, is_debug=True):
        self.orig_img = img
        self.debug_img = img
        self.is_face = False
        self.landmarks_6 = 0
        self.landmarks_all = 0
        self.relevant_locations = [36, 39, 42, 45, 48, 54]
        self.rotation_vector = np.zeros(3)
        self.translation_vector = np.zeros(3)
        self.is_debug = is_debug
        self.gaze_origin = 0
        self.net_input = 0
        self.img_for_net = 0
        self.head_pose_for_net = 0

    def flip(self):
        self.debug_img = cv2.flip(self.debug_img, 1)

    def get_eye_centers(self):
        shape = self.landmarks_6

        rcenter_x = (shape[0][0] + shape[1][0]) / 2
        rcenter_y = (shape[0][1] + shape[1][1]) / 2

        lcenter_x = (shape[2][0] + shape[3][0]) / 2
        lcenter_y = (shape[2][1] + shape[3][1]) / 2

        lcenter = tuple([rcenter_x, rcenter_y])
        rcenter = tuple([lcenter_x, lcenter_y])
        return rcenter,lcenter

    def get_landmarks(self, shape):
        num = 68
        list = range(num)
        coords = np.zeros((num, 2), dtype="float32")
        j = 0
        for i in list:
            coords[j] = (shape.part(i).x, shape.part(i).y)
            j = j + 1
        return coords

    def face_landmark_detect(self, head_loc=None):
        if head_loc is not None:
            return True
        gray = cv2.cvtColor(self.orig_img, cv2.COLOR_BGR2GRAY)
        rects_cv = face_cascade.detectMultiScale(gray)

        if np.size(rects_cv) > 0:
            rects_cv_to_dlib = dlib.rectangle(rects_cv[0][0], rects_cv[0][1], rects_cv[0][0] + rects_cv[0][2],
                                              rects_cv[0][1] + rects_cv[0][3])
            prediction = predictor(gray, rects_cv_to_dlib)
            self.landmarks_all = self.get_landmarks(prediction)
            self.landmarks_6 = self.landmarks_all[self.relevant_locations]
            image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            for (x, y) in self.landmarks_6:
                cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
            cv2.imshow("Output", image)
            cv2.waitKey(0)
            self.is_face = True
        return self.is_face

    def head_pose_detect(self, head_loc=None):
        if head_loc is None:
            landmarks = self.landmarks_6
        else:
            landmarks = head_loc
        mini_face_model_adj = LANDMARKS_6_PNP.T.reshape(LANDMARKS_6_PNP.shape[1], 1, 3)
        dist_coeffs = utils.global_camera_coeffs
        camera_matrix = utils.global_camera_matrix
        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs,
                                                                                True)

        (success, self.rotation_vector, self.translation_vector) = cv2.solvePnP(mini_face_model_adj, landmarks,
                                                                                camera_matrix,
                                                                                dist_coeffs, self.rotation_vector,
                                                                                self.translation_vector,
                                                                                True)

    def create_show_img(self,pitchyaw):
        r_eye_center , ___  = self.get_eye_centers()
        img = utils.draw_gaze(self.orig_img, eye_pos=r_eye_center, pitchyaw=pitchyaw)
        for (x, y) in self.landmarks_6:
            cv2.circle(img, (x, y), 1, (0, 255, 0), -1)
        return img