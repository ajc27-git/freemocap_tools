from dataclasses import Field, dataclass


@dataclass
class BodyDimensions:
    total_height: float #"Total height of the body from the foot to the top of the head (m)
    total_wingspan: float #"Total wingspan of the body from L fingertip to R fingertip (m)
    mean_foot_length: float #Mean foot length from toe to heel (m)


