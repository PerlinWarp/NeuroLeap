## 8th of April 12:00
Made an initial model to predict the position of the thumb.   
  
![Comically Bad Thumb Model](media/FirstThumbModel.gif)
  
The above model uses a 4 layer dense neural network to predict the position of the thumb away from the Leap motion. 
This model was the first one I made and helped me build some infrastructure and workflow to build a serious model. 
I did not want to spend days making a low error model without being able to see if the basics I have work. Now I have the basic setup done, I know it works and can iterate on making it better.   
  
As this model predicts the absolute position of the thumb in space but not the relative position of the top of the thumb to another point on my arm, such as my palm. The model will always be wrong if my predictions are made with my hand further away from the leap motion than the data in the test set.  