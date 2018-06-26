Research for a stylist algorithm
================================

This research consists of a few simple Google searches, which in no way gives a complete picture.
The intent is to quickly find an approach on how to automize some of the knowledge that stylists have.
Not with the goal to replace their work, but to help boost second hand sales to spare the environment.

Most theories about beauty that I came accross take into account the color of eyes, skin and hair.
I'll first summarize some basics regarding this.

After that I'll describe two approaches on how to capture the colors and how we can represent them mathematically.

Then I'll list the theories about how the colors of eye, hair and skin relate to the optimal colors for clothing.
I'll start with the most simple theory and build up in complexity. 

Basics of color in appearence
-----------------------------

#### Eye color

An eye can have the combination between any of these colors:
* brown
* blue
* green
* grey

All these colors come in light and dark shades except grey, which is a shade in itself.
This info comes from [Kleur Analist](https://www.kleuranalist.nl/2013/10/kleureffect-ogen/#kleureffect-van-kleding)

However Wikipedia holds a different more complex definition as you can [read here](https://en.wikipedia.org/wiki/Eye_color)
The definition above seems more practical for now. No need to have names for color combinations or take into account special medical cases.

This is a nice schematic for the possible color possibilities:

![eye colors](https://styleconsulting.nl/media/3210/eye-colours.jpg?width=568&height=185)

#### Hair color

The color for hair seems to be a lot less complex than eye color. Probably because there are true pigments involved (unlike eye color where color is often a light scattering effect).
According to [this article](https://en.wikipedia.org/wiki/Eye_color#Amber) possible hair colors are:
* Black
* Brown
* Blond
* Auburn (brown-red)
* Red
* Grey
* White

It is actually hard to take into account grey hair. None of the theories that I've read so far is mentioning that case. Weird. Some people speak of "chestnut" here. 
As that is qualified as "brown-red" I'll assume it is the same as Auburn. 

#### Skin color

This is the most simple definition and probably the politically most sensitve. There are only three types [according to Wikipedia](https://en.wikipedia.org/wiki/Human_skin_color)
* Dark
* Light

Within light there is "Europe" and "Asian" colors, which are controlled by a separate set of genes. A skin color can "tan", which is a phenomena tight to several genes. 


Capturing color strategies
--------------------------

There is the [Beta Face API](https://www.betafaceapi.com/wpa/index.php/demo), which returns skin, eye and hair color as a hex value.
This is the simplest way of getting skin, eye and hair color, but it only returns one color and we can't tweak any parameters. 
We'll have to take these values as is and hope the API does not get easily fooled.
Due to the unclear background of the company offering the API, this approach is also a possible risk for the privacy of users.

There is no real quick alternative. There are a lot of companies that offer face detection and return landmarks. 
These landmarks consist of eyes, eyebrows, nose, mouth and chin coordinates. I haven't encountered services that return the position of hair in an image.
Some Googling revealed that several research papers have looked into this, but that would mean that we have to invest in replicating that research.
The easiest thing to try is to install and run [this repo](https://github.com/akirasosa/mobile-semantic-segmentation). 
It's hard to predict how well this will work, but it seems to follow the latest developments concerning such tasks as this (image segmentation).

#### Color representation

In general I think that the HSV color representation will be easiest to use, because it most closely approaches our "color circle".
The beauty experts often name colors. So it's going to be hard sometimes to figure out what they mean.
Changes to colors indicated by words like "darker", "lighter" and "brighter" are probably best interpreted as changes to saturation and value for HSV colors.
Depending on the theory it might be convenient to choose a different representation. All data is stored as RGB currently so working with RGB might save some time. 

Theories of color & beauty
--------------------------

####Eye matching

The simplest theory is that colors matching your eyes bring out your eyes more.
Especially tops like shirts and scarfs should match the color of your eyes to bring out "the jewelry that you can not change about yourself" 

The entire idea is maybe best captured with this image:

![eye color matching](https://styleconsulting.nl/media/3197/img-set.jpeg?anchor=center&mode=crop&width=850&height=405&format=jpg&quality=100&bgcolor=fff&rnd=131511878000000000)

####Color matching and contrasting

If you divide the color circle in 12 different colors (or 10 or 20 because HSV is 360 colors?). You get an image like

![color circle segments](https://styleconsulting.nl/media/3233/img-set-3.jpeg?width=500&height=500) 


Monochromastic colors are colors within the same segment, but with a different tone. This could mean variations in saturation and value or slight variations within the segment of hue.
Monochromastic colors are called "ton sur ton" by the beauty industry.
Colors one segment next to a segment are the "analogic" colors for that segment (which make up a low contrast color palette together).
Colors directly opposite are high contrast colors.
You can also choose the analog colors of the contrast color to slightly dim down the contrast.

More complex color matching patterns are matching 3 different colors (which should be equally divided among the circle) or 4 different colors (consisting of 2 pairs of colors analog to each other)
Especially the forth seems hard to achieve with computer code.  

####Technically simple (but racist?) theory

In the table below you see recommandations from [Mon Style](https://monstyle.nl/welke-kleuren-bij-welke-huidskleur/).
They define 6 types. More than half of them are Western, with two distinct types of blondes.
The good thing about this theory is that it seems easy to implement it with computer code.

| Skin, eyes and hair | Color recommendations | Forbidden colors |
| --- | --- | --- |
| Light skin, hair and eyes | Greys, pastel colors | Yellow |
| Light skin & hair, dark eyes | Warm colors, high saturation (dark) | White, cold pastel colors |
| Light skin & eyes, dark hair | Bright and dark colors | Unspecified |
| Light skin & eyes, red hair | Natural and dark colors | Red |
| Darker skin, hair and eyes | Natural and bright colors. Yellow and white | Almost any color goes |
| Dark skin, hair and eyes | The brighter and lighter the better | Pastel and greys |

In code we would have to define a division between warm and cold colors in hue. The pastel and bright colors can be separated within the saturation spectrum I think.
A dark or light color should have a treshold in value.
Particular colors as well as the greyscale would have to be determined from hue and equal rgb values.

####Season type


Apparently the combination between skin, hair and eye color is an indication for your "season type".
This is the more complicated color matching theory and I haven't worked it out in detail in this document.
I just scratch the surface to give an idea where this could lead to.

Below is a data structure that examplifies autumn and its color properties.

```json
{
    "autumn": {
        "skin": ["ivory"],
        "hair": ["auburn", "chestnut"],
        "eyes": ["dark brown", "greenish brown"]
    }
}
```

These seasons have certain color palettes attached to them. So depending on your type certain colors will suit you.
In one of these theories the colors for types get divided in a way that is easily translated in code. 
The color division runs across the warm and cool and bright and pastel dimensions as in the table below.

|            | Warm   | Cold   |
| -----------| -------|--------|
| **Bright** | Spring | Winter |
| **Pastel** | Autumn | Summer | 

Technically the division between warm and cold is a division in hue and the division in bright and pastel colors is a division in saturation.

Some colors fit every person, because they occupy the center in both hue and saturation dimensions.
One example color is denim blue.

The following sources explain the season types in detail and offer alternative color palettes:
* [Girl Scene](https://www.girlscene.nl/artikel/10100-kleurenanalyse-welke-kleuren-staan-bij-jou)
* [Color Me Pretty](https://www.colormepretty.co/categories-2/4-season-color-analysis/)
* [Koffie tijd](https://www.koffietijd.nl/welk-kleurtype-ben-jij)
* [Kleding Styliste](http://kledingstyliste.nl/kleurtypes/kleurtypes-welke-kleur-past-bij-jou/#gallery-2)


Facial contrast and outfit contrast
-----------------------------------

The [Kleding Styliste](http://kledingstyliste.nl/kleurtypes/kleurtypes-welke-kleur-past-bij-jou/#gallery-2) poses a different theory, which is more or less complementary to theories above.
The theory is summarized in a few simple rules that I'll write down here:

* Dark colors look good on people with dark hair
* Light colors look good on people with light hair
* Dark hair with light eyes requires a dark outfit with light accents
* If your eyes, hair and skin have a low contrast you should wear a low contrast outfit
* If your eyes, hair and skin have a high contrast you should wear a high contrast outfit
* Low contrast eyes, hair and skin fit pastel colors
* High contrast eyes, hair and skin fit bright colors
* Do not wear large dark pieces of cloths when you have light hair and dark eyes, but small dark patches instead.




Body shape
----------

This is another beauty theory that I found, which does not look at color at all. 
The [body shape theory](https://www.assem.nl/berry/artikel/welke-kleding-past-bij-mijn-figuur).
Implementing this theory is probably the hardest as it requires detecting body features that are much more complex than colors of body parts. 
