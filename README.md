This is the code for a simple game,
which is based on the interaction with hardware inputs.
Basically the game is programmed as a state machine where
the states serve as individual levels.
The game was implemented for a
[BeagleBone Black](http://beagleboard.org/black), so all directly
hardware related files are specific to this, but as the level of abstraction
is quite high it should be fairly easy to port the code to a different
hardware.

The basic working principle is a state machine as mentioned. A state
is at least defined by a name, next state and a list of conditions for
entering the next state. In addition the framework provides the
posibility to call arbitrary function when entering and leaving a state.
Furthermore the user can pass a function which is executed in parallel
in the state in a separate thread.

Conditions are supplied via either the AnalogCondition class which can be
used to check for a condition equal, bigger or smaller to a threshold of
an analog device or via the DigitalCondition class for binary choices.

The feature list also includes the following gimmicks:

    - Central soundserver with play queue
    - GUI program to mock the hardware with sliders and buttons to be able
    to program without having access to real hardware

In this framework a full 6 level game can be written as simply
as:

    states =
            {0: State('Align Mirror',
                       AnalogCondition(photo_diode, threshold=0.4, condition='bigger',
                                       hold_true=hold_time, debug=debug), next_states=[1, 1]),

              1: State('Change Cavity Length',
                       AnalogCondition(cavity_poti, condition='equal', equal_epsilon=0.03,
                                       threshold=0.7, hold_true=hold_time, debug=debug),
                       next_states=[2, 2], parallel_actions=[(cavity_resonant_blinking,
                                                              (cavity_blue_led, cavity_green_led,
                                                               cavity_poti))]),

              2: State('Trap Atom',
                       AnalogCondition(photo_diode, threshold=0.15, hold_true=hold_time,
                                       condition='smaller', debug=debug), next_states=[3, 3]),

              3: State('Tune Frequency Blocking',
                       AnalogCondition(laser_poti, condition='equal', equal_epsilon=0.1,
                                       threshold=0.2, hold_true=hold_time, debug=debug), next_states=[4, 2],
                       fail_probability=0.02, random_actions=[(kick_out_atom, atom_eject_servo)],
                       parallel_actions=[(blink_randomly, (spcm_0_led, spcm_1_led))]),

              4: State('Tune Frequency Conjunct Tunneling',
                       AnalogCondition(laser_poti, condition='equal', equal_epsilon=0.1,
                                       threshold=0.7, hold_true=hold_time, debug=debug),
                       parallel_actions=[(blink_alternating, (spcm_0_led, spcm_1_led))], next_states=[5, 5]),
              5: State('Success', False, next_states=[5, 99],
                       parallel_actions=[(blink_together, (spcm_0_led, spcm_1_led))]),
              }

Have fun building own games!
