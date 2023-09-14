from dataclasses import dataclass
from typing import Callable, ClassVar, Dict, List, Union, Tuple
import inspect
import numpy as np

from quam_components.core import QuamComponent


__all__ = [
    "Pulse",
    "MeasurementPulse",
    "ReadoutPulse",
    "DragPulse",
    "SquarePulse",
    "GaussianPulse",
]


@dataclass
class Pulse(QuamComponent):
    operation: ClassVar[str] = "control"
    length: int

    digital_marker: ClassVar[Union[str, List[Tuple[int, int]]]] = None

    def get_pulse_config(self):
        assert self.operation in ["control", "measurement"]
        assert isinstance(self.length, int)

        pulse_config = {
            "operation": self.operation,
            "length": self.length,
            "waveforms": {},
        }
        if self.digital_marker is not None:
            pulse_config["digital_marker"] = self.digital_marker

        return pulse_config

    def _get_waveform_kwargs(self, waveform_function: Callable = None):
        if waveform_function is None:
            waveform_function = self.waveform_function

        return {
            attr: getattr(self, attr)
            for attr in inspect.signature(waveform_function).parameters.keys()
            if attr not in ["self", "operation", "args", "kwargs"]
        }

    def calculate_integration_weights(self) -> Dict[str, np.ndarray]:
        # Do nothing by default, allow subclasses to add integration weights
        ...

    def calculate_waveform(self):
        kwargs = self._get_waveform_kwargs()
        waveform = self.waveform_function(**kwargs)

        # Optionally convert IQ waveforms to complex waveform
        if isinstance(waveform, tuple) and len(waveform) == 2:
            if isinstance(waveform[0], (list, np.ndarray)):
                waveform = np.array(waveform[0]) + 1.0j * np.array(waveform[1])
            else:
                waveform = waveform[0] + 1.0j * waveform[1]

        return waveform

    @staticmethod
    def waveform_function(**kwargs) -> List[Union[float, complex]]:
        """Function that returns the waveform of the pulse.

        Can be either a list of floats, a list of complex numbers, or a tuple of two
        lists.
        This function is called from `calculate_waveform` with the kwargs of the
        dataclass instance as arguments. Each kwarg should therefore correspond to a
        dataclass field.
        """
        raise NotImplementedError("Subclass pulses should implement this method")


@dataclass
class MeasurementPulse(Pulse):
    operation: ClassVar[str] = "measurement"

    digital_marker: ClassVar[str] = "ON"


@dataclass
class ReadoutPulse(MeasurementPulse):
    amplitude: float
    rotation_angle: float = None

    def calculate_integration_weights(self):
        integration_weights = {
            "cosine": {
                "cosine": [(1.0, self.length)],
                "sine": [(0.0, self.length)],
            },
            "sine": {
                "cosine": [(0.0, self.length)],
                "sine": [(1.0, self.length)],
            },
            # Why is there no minus cosine?
            "minus_sine": {
                "cosine": [(0.0, self.length)],
                "sine": [(-1.0, self.length)],
            },
        }
        if self.rotation_angle is not None:
            integration_weights["rotated_cosine"] = {
                "cosine": [(np.cos(self.rotation_angle), self.length)],
                "sine": [(-np.sin(self.rotation_angle), self.length)],
            }
            integration_weights["rotated_sine"] = {
                "cosine": [(np.sin(self.rotation_angle), self.length)],
                "sine": [(np.cos(self.rotation_angle), self.length)],
            }
            integration_weights["rotated_minus_sine"] = {
                "cosine": [(-np.sin(self.rotation_angle), self.length)],
                "sine": [(-np.cos(self.rotation_angle), self.length)],
            }
        return integration_weights

    def waveform_function(self, amplitude):
        # This should probably be complex because the pulse needs I and Q
        return complex(amplitude)


@dataclass
class DragPulse(Pulse):
    rotation_angle: float
    amplitude: float
    sigma: float
    alpha: float
    anharmonicity: float
    detuning: float = 0.0
    subtracted: bool = True

    @staticmethod
    def waveform_function(
        length,
        amplitude,
        sigma,
        alpha,
        anharmonicity,
        detuning,
        subtracted,
        rotation_angle,
    ):
        from qualang_tools.config.waveform_tools import drag_gaussian_pulse_waveforms

        I, Q = drag_gaussian_pulse_waveforms(
            amplitude=amplitude,
            length=length,
            sigma=sigma,
            alpha=alpha,
            anharmonicity=anharmonicity,
            detuning=detuning,
            subtracted=subtracted,
        )
        I, Q = np.array(I), np.array(Q)

        rotation_angle_rad = np.pi * rotation_angle / 180
        I_rot = I * np.cos(rotation_angle_rad) - Q * np.sin(rotation_angle_rad)
        Q_rot = I * np.sin(rotation_angle_rad) + Q * np.cos(rotation_angle_rad)

        return I_rot + 1.0j * Q_rot


@dataclass
class SquarePulse(Pulse):
    amplitude: float

    @staticmethod
    def waveform_function(length, amplitude):
        return amplitude


@dataclass
class GaussianPulse(Pulse):
    ampltiude: float
    length: int
    sigma: float

    def waveform_function(
        amplitude,
        length,
        sigma,
        subtracted=True,
    ):
        t = np.arange(length, dtype=int)  # An array of size pulse length in ns
        center = (length - 1) / 2
        gauss_wave = amplitude * np.exp(
            -((t - center) ** 2) / (2 * sigma**2)
        )  # The gaussian function
        if subtracted:
            gauss_wave = gauss_wave - gauss_wave[-1]  # subtracted gaussian
        return gauss_wave
