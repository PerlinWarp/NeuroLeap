# NeuroLeap  
  
Leap Motion Hello world:  
```
sudo leapd
python3 plot_hand.py
```
  
Myo Hello World:  
```
python3 myo_raw.py
```
Plots Myo data, note the Myo sensor with the LED is the 4th graph from the top.  
You can confirm this by sliding your fingers under each sensor and watching each graph change.  
  
[Generating a python wrapper for the leap motion.](https://support.leapmotion.com/hc/en-us/articles/360004362237-Generating-a-Python-3-3-0-Wrapper-with-SWIG-2-0-9)

## Info  
To see model development and an overview of the decisions I made while making models see [modelProgress.md](docs/modelProgress.md).  
  
For model development, see the Notebooks folder. If they don't render in GitHub the first time, keep retrying until they do.  
  
## Files and folders  
  
NeuroLeap.py - Contains functions used for getting, plotting, saving and interpreting data from the Myo and Leap.  
  
make_dataset.py - Uses data_gather.py to read data from a single Myo and Leap motion until a time limit is reached, then saves the Myo and Leap data into one CSV file. The Leap motion data is plotted in the main thread to monitor the quality of the Leap Motion data.
  
data_gather.py - Used by other scripts to connect and gather data from a single Myo and pass this data back to the main script using a multiprocessing array.
  
plot_hand.py - Live plots 22 points of the hand gathered from the Leap Motion using Matplotlib.
  
animate_saved.py - Animates gathered LeapMotion data, useful to see exactly what gestures were performed in each dataset.
  

