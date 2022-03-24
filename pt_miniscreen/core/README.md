# Miniscreen Core

Core API for building efficient and scalable miniscreen applications. The API is
intentionally minimal, focusing on small reusable classes that only have methods
that are essential and / or address common areas of difficulty.

## App

The App class is used to start and stop the application and show produced images
on the OLED display. It takes a miniscreen instance and a root Component class.

### Examples

To use the miniscreen instance a new App class should be created that inherits
from this base class. The subclass can then register button handlers and call
methods defined on the root Component class:

```python3
from pt_miniscreen.core import App

class MiniscreenApp(App):
  def __init__(self, miniscreen)
    super().__init__(miniscreen, Root=Counter)

    miniscreen.select_button.when_released = self.when_select_button_released

  def when_select_button_released(self):
    self.root.increment()
```

## Component

The Component class is where the majority of the application logic lives.

Components:

- define a render method, which takes an image and returns an image.
- define the state needed to render an image
- optionally create child components to be used in the render method.
- optionally create intervals to update state regularly.
- notify parents of a rerender due to a state change or a child rerender

Allowing components to own child components allows us to build a tree of
components. This makes the heirarchy of the app flexible as every layer
is composable with every other layer. Having a single abstraction handle
layout and rendering makes the app easier to understand as well.

When a component calls self.state.update it reconciles, which is when it
checks if the output from render has changed and then notifies it's
parent of the rerender if needed. When a child component rerenders the
parent also reconciles itself, this propogates up the tree until either
a parent's output is unchanged or the app displays the resulting image.

To prevent concurrent state updates from causing unexpected behaviour
there is a reconciliation lock per component. This means a parent only
handles a single state update or child rerender at a time. It combines
updates that occur during a reconciliation so that only one subsequent
reconciliation is required to be fired even when many updates happen at
once. This works well for cases when there are a small to medium number
of threads and children per component which is expected to be true in
the majority of cases.

The render method is memoised by default: if it is invoked with the same
image it will return the cached output. This means parents can call a
child's render method frequently without overhead assuming the input
image is unchanged. Combined with the fact that rerenders are triggered
by state changes static components such as text or images have very
little overhead.

Creating intervals to update state within a component was added to
allow for concurrency without exposing the user to full threading.
Intervals created this way are also automatically cleaned up and prevent
circular references and therefore memory leaks being created.

### Examples

#### Rendering

The simplest possible component only defines a render method. The render method
takes an image and returns an image. It's safe to mutate the image passed in but
you must return an image or nothing will be displayed on the screen.

```python3
from PIL import ImageDraw
from pt_miniscreen.core import Component

class Box(Component):
  render(self, image):
    # draw the outline of a rectangle on the passed image
    draw = ImageDraw.Draw(image)
    draw.rectangle(((0, 0), image.size), outline="white")

    # return the updated image
    return image
```

#### Setup

It is often a good idea to do something when a component is created. To do this
override the `__init__` method and add the logic you need there. When doing this
it's very important to pass keyword arguments through to super so that the
component still works:

```python3
from pt_miniscreen.core import Component

class HelloWorld(Component):
  # use **kwargs to get keyword arguments
  def __init__(self, **kwargs)
    # setup Component by passing **kwargs to super
    super().__init__(**kwargs)

    # custom logic here
```

It's also possible to define custom arguments for your component:

```python3
from pt_miniscreen.core import Component

class HelloWorld(Component):
  def __init__(self, custom_argument=None, **kwargs)
    # don't forget to pass **kwargs to super
    super().__init__(**kwargs)

    # Do something with custom_argument
```

#### State

Applications that don't render a static image need state. To keep the rendered
image in sync with your component state it must live in a special `self.state`
dictionary. To tell a component that state has changed and it should rerender
it's image you must use the `self.state.update` method.

```python3
from pt_miniscreen.core import Component
from pt_miniscreen.utils import get_font

class Counter(Component):
  # define a `default_state` dictionary to create state with known values
  default_state = {"count": 0}

  def increment(self):
    # use `self.state.update` to change state and rerender the rendered image
    self.state.update({"count": self.state["count"] + 1})

  def render(self, image):
    # state lives on `self.state` and is accessed like a normal dictionary
    text = str(self.state["count"])

    PIL.ImageDraw.Draw(image).text(
      text=text,
      font=get_font(),
      fill="white"
    )

    return image
```

#### Custom Initial State

Sometimes you want the parent to define the initial state of a child component.
To do this you can override the component's `__init__` method as seen in
[setup](#setup).

```python3
from pt_miniscreen.core import Component
from pt_miniscreen.utils import get_font

class Counter(Component):
  # setup a custom argument when overriding `__init__`
  def __init__(self, initial_count=0, **kwargs):
    # use custom argument to create `initial_state` dictionary
    super().__init__(**kwargs, initial_state={
      "count": initial_count
    })

  ...
```

#### Child Components

To use other components in your component you need to create them using the
`create_child` method. Once a component has been created you can pass images
to it's render method. It is usually a good idea to create the children you
need during setup.

```python3
from pt_miniscreen.core import Component
from pt_miniscreen.components import Text

class HelloWorld(Component):
  def __init__(self, **kwargs)
    # setup Component so that the `create_child` method works
    super().__init__(**kwargs)

    # to create a child pass a component's class to the first argument of
    # `create_child`. Add any arguments you need to pass to the component as
    # additional arguments. Store the child in an attribute, in this case
    # "hello_world_text", so that it can be used in the render method!
    self.hello_world_text = self.create_child(Text, text="Hello World!")

  def render(self, image):
    # Pass the image you want the child to render on top of into it's render method.
    # Components know their size based on size of the image passed to render.
    padding = 10
    return self.hello_world_text.render(image.crop(
      (padding, padding, image.height - padding, image.width - padding)
    ))
```

#### Intervals

An interval is when a method is called after a certain amount of time over and
over again. This is useful if you want to keep something up to date, or if you
need to update some value at regular intervals. To create an interval you can
use the `create_interval` method.

```python3
from pt_miniscreen.core import Component
from pt_miniscreen.components import Text

class Timer(Component):
  default_state = {"seconds": 0, "hours": 0}

  def __init__(self, **kwargs)
    # setup Component so that the `create_interval` method works
    super().__init__(**kwargs)

    # pass the method you want called to `create_interval`. By default it runs
    # the method every second.
    self.create_interval(self.increment_seconds)

    # the second argument is the time to wait between method calls
    self.create_interval(self.increment_hours, 3600)

  def increment_seconds(self):
    self.state.update({"seconds": self.state["seconds"] + 1})

  def increment_hours(self):
    self.state.update({"hours": self.state["hours"] + 1})

  def render(self, image):
    hours = self.state["hours"]
    seconds = self.state["seconds"]

    PIL.ImageDraw.Draw(image).text(
      text=f"{hours}h {seconds}s",
      font=get_font(),
      fill="white"
    )

    return image
```

## Components

Common components have been added to the components folder. These
components include equivalents of the Text, MarqueeText and Image
hotspots and adds new List, PageList, and Stack components.

## Utils

Utils for rendering, positioning, fonts and performing timed transitions
have been added to help with common and/or difficult use-cases.

The core is also built with the intention of exposing it through the SDK
eventually.
