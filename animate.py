import matplotlib.pylab as plt
from matplotlib import animation

FPS = 12
FRAMES = range(30,90) # iterator for animate function
FILENAME = 'basic_animation.mp4'

# Create fig and axes
fig, ax = plt.subplots(figsize=(20,10))

def animate(i):
  ax.clear() # Clear ax (use if each frame is redrawn from scratch)
  # Draw plot
  # ax.plot ...
  # ax.plot ...

# Render video
anim = animation.FuncAnimation(fig, animate, frames=FRAMES , interval=20)
writervideo = animation.FFMpegWriter(fps=FPS)
anim.save(FILENAME, writer=writervideo)
plt.close()