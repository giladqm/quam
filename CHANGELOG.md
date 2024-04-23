## [Unreleased]
### Fixed
- Fix error where a numpy array of integration weights raises an error
- Fix instantiation of a dictionary where the value is a reference

## [0.3.1]
### Added
- Add optional `config_settings` property to quam components indicating that they should be called before/after other components when generating QUA configuration
- Added `InOutIQChannel.measure_accumulated/sliced`
- Added `ReadoutPulse`. All readout pulses can now be created simply by inheriting from the `ReadoutPulse` and the non-readout variant.
- Added `Channel.set_dc_offset`

### Changed
- Pulses with `pulse.axis_angle = None` are now compatible with an `IQChannel` as all signal on the I port.

### Fixed
- Switched channel `RF_inputs` and `RF_outputs` for Octave
- Loading QuAM components when the expected type is a union or the actual type is a list
  no longer raises an error
- The qua config entries from OctaveUpConverter entries I/Q_connection were of type 
  QuamList, resulting in errors during deepcopy. Converted to tuple

## [0.3.0]
### Added
- Added InOutSingleChannel
- Added optional `config_settings` property to quam components indicating that they should be called before/after other components when generating QUA configuration
- Added support for the new Octave API.
- Added support for `Literal` types in QuAM

### Changed
- Changed `InOutIQChannel.input_offset_I/Q` to `InOutIQChannel.opx_input_offset_I/Q`
- Renamed `SingleChannel.output_offset` -> `SingleChannel.opx_output_offset`
- Pulse behaviour modifications to allow pulses to be attached to objects other than channels. Changes conist of following components
  - Added `pulse.channel`, which returns None if both its parent & grandparent is not a `Channel`
  - Rename `Pulse.full_name` -> `Pulse.name`.
    Raises error if `Pulse.channel` is None
    TODO Check if this causes issues
  - `Pulse.apply_to_config` does nothing if pulse has no channel
- Raise AttributeError if channel doesn't have a well-defined name.
  This happens if channel.id is not set, and channel.parent does not have a name either
- `Pulse.axis_angle` is now in radians instead of degrees.
- Channel offsets (e.g. `SingleChannel.opx_output_offset`) is None by default (see note in Fixed)
- Move `quam.components.superconducting_qubits` to `quam.examples.superconducting_qubits`
- Replaced `InOutIQChannel.measure` kwargs `I_var` and `Q_var` by `qua_vars` tuple
- `Pulse.id` is now an instance variable instead of a class variable
- Channel frequency converter default types are now `BaseFrequencyConverter` which has fewer attributes than `FrequencyConverter`. This is to make it compatible with the new Octave API.

### Fixed
- Don't raise instantiation error when required_type is not a class
- Add support for QuAM component sublist type: List[List[...]]
- Channel offsets (e.g. `SingleChannel.opx_output_offset`) are ensured to be unique, otherwise a warning is raised
  - Previously the offset could be overwritten when two channels share the same port
  - Default values are None, and they're only added if nonzero
  - If the offset is not specified in config at the end, it's manually added to be 0.0
- JSON serializer doesn't break if an item is added to ignore that isn't part of QuAM
- Allow `QuamDict` keys to be integers

## [0.2.2] -
### Added
- Overwriting a reference now raises an error. A referencing attribute must first be set to None

## [0.2.1] -
This release primarily targets Octave compatibility
### Changes
- `FrequencyConverter` and `LocalOscillator` both have a method `configure()` added
- Improve documentation of `IQChannel`, `InOutIQChannel`
- Various fixes to Octave, including removal of any code specific to a single QuAM setup
- Allow `expected_type` in `instantiate_attrs` to be overridden when `__class__` is provided.
- Remove `_value_annotation` when calling `get_dataclass_attr_annotation`
- Slightly expanded error message in `validate_obj_type`

## [0.2.0] -
### Changed
- Quam components now user `@quam_dataclass` decorator instead of `@dataclass(kw_only=True)`

## [0.1.1] -
Only registering changes from November 29th

### Added
- Add `Pulse.axis_angle` for most pulses that specifies axis on IQ plane if defined
- Add `validate` kwarg to `pulse.play()`
- Add `InOutIQChannel.measure()`
- Add `ArbitraryWeightsReadoutPulse`

### Changed
- `InOutIQChannel.frequency_converter_down` default is None
- Change `ConstantReadoutPulse` -> `ConstantWeightsReadoutPulse`

### Fixed