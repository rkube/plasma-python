Primitives
==========

FRNN defines abstractions for fusion devices, measurements, and signals to better work with large datasets.

Machines
--------
The abstraction of a fusion device is called a machine. Besides defining the range of valid 
measurements, a machine most prominently defines a method to access measurements.
FRNN creates a class hierarchy of machines. The abstract basis class :class:`plasma.primitives.machine.Machine`
defines the interface. Actual machines implemented are 

* JET, :class:`plasma.primitives.machine.MachineJET`
* D3D, :class:`plasma.primitives.machine.MachineD3D`
* NSTX, :class:`plasma.primitives.machine.MachineNSTX`


The method :meth:`plasma.primitives.machine.fetch_data` is the interface to fetch data for a given
machine. A signal path, a shot number, 



Signals
-------
Signals represents measurement of a certain quantity on a given machine.
Their implementation is given in :class:`plasma.primitives.signal.Signal`

This class allows to fetch data for the signal in general, for various shots.
In this sense, it provides an access mechanism for this data.
The `Signal` class also provides mechanisms to check the validity of the data
as well as other quantities, such as whether it is positive, etc.

Signals are agnostic to machines. That is, a single signal instance represents the 
signal on different machines. The constructor takes the argument `machines` which is
a list of :class:`plasma.primitive.machine` instances. 

The main interface to load signal data is :meth:`plasma.primitives.signal.load_data`. This is
true for the base class as well as all derived classes. Internally, these methods first call
:meth:`plasma.primitives.signal._load_data_from_txt_safe`, which fetches data as a numpy array
 from file and performs additional error checking.

The main


Currently there are multiple methods to load data:
* load_data_from_txt_safe
* load_data 
* fetch_data_basic 
* fetch_data 

This should be slimmed down. Or at least explain what the difference between these four are.



Shots
------
Each shot is a measurement of plasma current as a function of time. The Shot objects contains following attributes:

 * `number` - integer, unique identifier of a shot
 * `t_disrupt` - double, disruption time in milliseconds (second column in the shotlist input file)
 * `ttd` - array of doubles, time profile of the shot converted to time-to-disruption values
 * `valid` - boolean, whether plasma current reaches a certain value during the shot
 * `is_disruptive` - boolean, whether the shot was determined to be disruptive by an expert

        
For 0D data, each shot is modeled as 2D array - time vs plasma current.

ShotLists
---------

Is a wrapper around list of shots. Therefore, it is a list of 2D arrays.

Sublists
--------

Shot lists is split into sublists having `num_at_once` shots from an entire dataset contained in ShotList. 

Patch
-----

The length of shots varies by a factor of 20. For data parallel synchronous training it is essential that amounds of train data passed to the model replica is about the same size.

Patches are subsets of shot time/signal profiles of equal length. Patch size is approximately equal to the minimum shot length (or the largest number less or equal to the minimum shot length divisible by the LSTM model length).

Since shot lengthes are not multiples of the min shot length in general, some non-deterministic fraction of patches is created.

Chunk
-----

A subset of `patch` defined as:
```
num_chunks = Length of the patch/ num_timesteps
```        
where `num_timesteps` is the sequence length fed to the RNN model.

Batch
-----

Mini-batch gradient descent is used to train neural network model.
`num_batches` represents the number of *patches* per mini-batch.

Batch input shape
-----------------

The data in batches fed to the Keras model should have shape:

```
batch_input_shape = (num_chunks*batch_size,num_timesteps,num_dimensions_of_data)
```

where `num_dimensions_of_data` is the signal dimensionality. For 0D dataset we only have a time profile of plasma current,
so `num_dimensions_of_data = 1`
