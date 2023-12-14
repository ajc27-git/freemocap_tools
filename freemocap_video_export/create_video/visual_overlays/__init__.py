from freemocap_video_export.create_video.visual_overlays.frame_information_dataclass import FrameInformation
from freemocap_video_export.create_video.visual_overlays.frame_number_overlay import VisualComponentFrameNumber
from freemocap_video_export.create_video.visual_overlays.image_overlays import VisualComponentImage, VisualComponentLogo
from freemocap_video_export.create_video.visual_overlays.json_table_overlays import VisualComponentStaticJSONTable, \
    VisualComponentRecordingParameters, VisualComponentMediapipeSkeletonSegmentLengths
from freemocap_video_export.create_video.visual_overlays.matplotlib_plot_overlays import VisualComponentPlotComBos, \
    VisualComponentPlotFootDeviation

VIDEO_OVERLAY_CLASSES = {
    'frame_number': VisualComponentFrameNumber,
    'logo': VisualComponentLogo,
    'static_json_table': VisualComponentStaticJSONTable,
    'recording_parameters': VisualComponentRecordingParameters,
    'mediapipe_skeleton_segment_lengths': VisualComponentMediapipeSkeletonSegmentLengths,
    'plot_com_bos': VisualComponentPlotComBos,
    'plot_foot_deviation': VisualComponentPlotFootDeviation,
    'image': VisualComponentImage,
}