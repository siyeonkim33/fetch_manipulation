; Auto-generated. Do not edit!


(cl:in-package pose_cnn-msg)


;//! \htmlinclude Class.msg.html

(cl:defclass <Class> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (objects
    :reader objects
    :initarg :objects
    :type (cl:vector pose_cnn-msg:EachObject)
   :initform (cl:make-array 0 :element-type 'pose_cnn-msg:EachObject :initial-element (cl:make-instance 'pose_cnn-msg:EachObject))))
)

(cl:defclass Class (<Class>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Class>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Class)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name pose_cnn-msg:<Class> is deprecated: use pose_cnn-msg:Class instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <Class>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pose_cnn-msg:header-val is deprecated.  Use pose_cnn-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'objects-val :lambda-list '(m))
(cl:defmethod objects-val ((m <Class>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pose_cnn-msg:objects-val is deprecated.  Use pose_cnn-msg:objects instead.")
  (objects m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Class>) ostream)
  "Serializes a message object of type '<Class>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'objects))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (roslisp-msg-protocol:serialize ele ostream))
   (cl:slot-value msg 'objects))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Class>) istream)
  "Deserializes a message object of type '<Class>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'objects) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'objects)))
    (cl:dotimes (i __ros_arr_len)
    (cl:setf (cl:aref vals i) (cl:make-instance 'pose_cnn-msg:EachObject))
  (roslisp-msg-protocol:deserialize (cl:aref vals i) istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Class>)))
  "Returns string type for a message object of type '<Class>"
  "pose_cnn/Class")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Class)))
  "Returns string type for a message object of type 'Class"
  "pose_cnn/Class")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Class>)))
  "Returns md5sum for a message object of type '<Class>"
  "2f93a459fd733d74310fa2e7ea67cf95")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Class)))
  "Returns md5sum for a message object of type 'Class"
  "2f93a459fd733d74310fa2e7ea67cf95")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Class>)))
  "Returns full string definition for message of type '<Class>"
  (cl:format cl:nil "###########################################################~%# This message describes an object.~%~%# Many of the geometric items below lack a stamp/frame_id,~%# header stamp/frame_id should be used there~%std_msgs/Header header~%~%EachObject[] objects~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: pose_cnn/EachObject~%###########################################################~%# This message describes an object.~%~%# An object might have a name~%string name~%~%# Poses of each object~%geometry_msgs/PoseStamped posestamped~%================================================================================~%MSG: geometry_msgs/PoseStamped~%# A Pose with reference coordinate frame and timestamp~%Header header~%Pose pose~%~%================================================================================~%MSG: geometry_msgs/Pose~%# A representation of pose in free space, composed of position and orientation. ~%Point position~%Quaternion orientation~%~%================================================================================~%MSG: geometry_msgs/Point~%# This contains the position of a point in free space~%float64 x~%float64 y~%float64 z~%~%================================================================================~%MSG: geometry_msgs/Quaternion~%# This represents an orientation in free space in quaternion form.~%~%float64 x~%float64 y~%float64 z~%float64 w~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Class)))
  "Returns full string definition for message of type 'Class"
  (cl:format cl:nil "###########################################################~%# This message describes an object.~%~%# Many of the geometric items below lack a stamp/frame_id,~%# header stamp/frame_id should be used there~%std_msgs/Header header~%~%EachObject[] objects~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: pose_cnn/EachObject~%###########################################################~%# This message describes an object.~%~%# An object might have a name~%string name~%~%# Poses of each object~%geometry_msgs/PoseStamped posestamped~%================================================================================~%MSG: geometry_msgs/PoseStamped~%# A Pose with reference coordinate frame and timestamp~%Header header~%Pose pose~%~%================================================================================~%MSG: geometry_msgs/Pose~%# A representation of pose in free space, composed of position and orientation. ~%Point position~%Quaternion orientation~%~%================================================================================~%MSG: geometry_msgs/Point~%# This contains the position of a point in free space~%float64 x~%float64 y~%float64 z~%~%================================================================================~%MSG: geometry_msgs/Quaternion~%# This represents an orientation in free space in quaternion form.~%~%float64 x~%float64 y~%float64 z~%float64 w~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Class>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'objects) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ (roslisp-msg-protocol:serialization-length ele))))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Class>))
  "Converts a ROS message object to a list"
  (cl:list 'Class
    (cl:cons ':header (header msg))
    (cl:cons ':objects (objects msg))
))
