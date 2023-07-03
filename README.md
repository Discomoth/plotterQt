# plotterQt
A QtPy application made to control plotting devices.

This is a completely prototype program and should be currently expected to act as such!
If something does not work, do not be surprised! Nothing is in a polished state yet. <br>

The design of this program was inspired by K40Whisperer. I really appreciated the easy interface used to control a complex device. Being able to manually jog the laser for placement of the burn was something I felt could be implemented with old HPGL controled pen plotters. Eventually these features will be implemented in plotterQt. It is a bit more challenging than I imaginged.

## Pretty important note
From @Discomoth:

Please make sure to log problems experienced with this program. This is a passion project but I want it to become something others can use to interact with pen plotters. I'll try and get to problem submissions, but please be patient. Include as much information as possible and actively work with me to help in instances where I cannot replicate the problem myself.

## Installation
**A word of warning to those using Windows:** This program was developed using a Linux operating system. Expect things to not work out of the box in a Windows environment.

To get things rolling, you'll need Python3 installed (preferably the most recent version available). <br>
The required python modules are:
* PyQt6
* serial
* future
* numpy
* six

These are all available for installation via the pip installer.

In the future these will be trimmed, as future and six are both required within the Python 3 port of chiplotle used by plotterQt. 

**This program leverages a submodule and symbolic link to allow access to chiplotle**

Setting up a submodule requires an extra step.

1. git clone --recurse-submodules [project link]
2. git checkout dev_chiplotle
3. cd into the plotterQt repository
4. git submodule update

That should populate the chiplote submodule! It might be trickier, so let me know how well this works for clean installations!

## Usage

### Introduction
This program currently is able to do a few things.
* Setup and manage pen plotter serial communications
* Handle customization of acceleration, pen force and other parameters
* Hangle multiple pens within a carousel
* Execute HPGL command based plots
* Sequence plotting actions and commands
* Page feed and repeat sequence actions

There are plenty of features to impelment, such as a plot stop function and multithreading so the GUI remains interactable. 

For now though, one should be able to run basic plots exported from Inkscape in HPGL format. More on that in a bit.

### Program startup
When the program starts, configuration prompts appear. You can wait and re-access these within the 'Config' action menu. 
Most of the GUI is placeholder for future functions. Things are not quite fully functional yet. 

To actually start plotting things, navigate to the 'Multiplot' tab. This will show a blank box with some select/add/remove options. This is where you add in the steps in the sequence that will be executed when the plot is run.

### Plot sequencing
The sequencer allows one to automate steps in the plotting process. Using multiple pens for plotting different colors can be heavily leveraged here. There are a series of elements that can be used to aid one in plotting. 

**Caution**: Sequence elements are not yet rearrangable or editable. Deleting and re-creating is currently the only way to rearrange or edit. Sorry! 

### Sequencing elements
* HPGL Plot Element
  * Select the file to plot and pens to execute the plot with. 
  * The Pen override option allows one to change pen parameters from those in the 'master' carousel settings. They are unique to the element and will not be saved. 
* Wait Element
  * Adds a user-selectable time delay
  * Great for allowing ink to dry
* Pause Element
  * Allows the user to stop the plot for utility purposes.
  * Great for setting up a new sheet on non-page feed plotters
  * Also good for changing pens on single or twin pen plotters
* Page Feed Element
  * Ejects the page on page-feed capable plotters. (HP 7550A)
* Chime Element
  * Not implemented yet!
  * Play a sound to alert user
* Repeat Element
  * Resets the completion flags of sequence elements and starts the plot from the beginning again. 
  * Might work mid sequence, but if it is placed in the middle, I really have no clue what will happen! Give it a try ;)

### Stopping a plot
This is something to be implemented in the future. The functionality is there, BUT the GUI needs to be multithreaded so the stop button can be pressed and issue the flag to stop the plot. 

For now, one can issue a 'CTRL + C' to the terminal session running the plot and it will stop the execution. Then the sequence can be edited, flags reset and restarted. 

### Reset Flags button
As the sequence is worked through, the steps are set to a 'complete' state. If the plot is interrupted part way though, some will be marked completed and some will not. In this state, if restarted, the sequence will resume at the first incomplete element. 

If the reset flags button is pressed, the completed steps will be reset to the original uncompleted state. 

