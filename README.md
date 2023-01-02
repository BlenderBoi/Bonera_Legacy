# Bonera

![Banner](https://user-images.githubusercontent.com/79613445/210190149-550c8269-55b4-4ecc-9057-e864ae49279e.png)

Bonera is an addon that provide a Set of Tool to Help to speed up the tedious part that is in the Manual Rigging Process.
The addon turned some of the more repetitive operator that sometimes solves using Simple Python script packed into a Toolkit Addon.

You Can Find Out All the Features in [Bonera Documentation](https://boneradocumentation.readthedocs.io/en/latest/index.html)

[BoneraDemo.webm](https://user-images.githubusercontent.com/79613445/210190272-f980053d-ab10-4adb-bb16-45cc81610f0b.webm)

Instead of a full rigging system, Bonera seeks to be the “Wrench and Screwdrivers” of your rigging process. Can be Useful if you have a wierdly specific things need to be done that is related in rigging.

![Panel](https://user-images.githubusercontent.com/79613445/210190159-f23afffc-53a3-4cf4-ae17-6fb2c4041e8b.png)


## Highlight Features

### Speed Up Hardsurface Rigging Workflow

When dealing with Hardsurface Rigging, often time one needs to deal with multiple objects.Creating Bones and Adding the Object’s Vertex to Vertex Group can be a really Time Consuming Process

By Using the Bone Chain From Object Hierarchy Operator in Object Mode, it creates a bone chain base on the object's hierarchy, You can set up bones quickly, especially for Hardsurface Model

[ObjectHierarchyDemo01.webm](https://user-images.githubusercontent.com/79613445/210190417-b325a3a0-02b9-4e78-a9d6-685f120fdca6.webm)

[ObjectHierarchyDemo02.webm](https://user-images.githubusercontent.com/79613445/210190427-043ba8f3-245f-480f-9e2a-311048127764.webm)



### Quickly Rig Curve Related Object

Curve Object are often used for things such as Hair, Grass, Ropes, Wires or any tube like items, While it is a very useful thing, rigging a rope involving Hooking Curve Points One By One, this can be very time consuming, and so this addon can help speed up this process

You Can Create the Bone in a Chain Like Manner Using Bone Chain From Curve

[BoneChainFromCurve.webm](https://user-images.githubusercontent.com/79613445/210190586-c3e02e73-7311-4b28-890a-5755fe454b75.webm)

### Apply Bone Shape Easily

Creating Bone Shape can be a Tedious Process, But most of the time, People Uses some a set of commonly used shape, Using Add / Apply Bone Shape, you can use Premade Bone Shape and Apply to Bones Speeding things Up.

You can Even add your Own Bone Shape by Adding your Own Widget in AddonDirectory/Bonera/Widget/

[ApplyBoneShape.webm](https://user-images.githubusercontent.com/79613445/210190606-75279c3a-24c1-4063-94bc-039709d2cc35.webm)

### Quick IK Setup

Quickly Set Up IK by using Generate IK to creates IK Controller Bone and / or Pole Bone quickly while set up the IK Constraint Quickly. 

[QuickIK.webm](https://user-images.githubusercontent.com/79613445/210190630-f9b34c8a-65d3-4157-83f0-8b21dee85294.webm)

### Create Bones From Selected

You Can use Create Bone from Selected to Quickly Create Multiple Bones in Edit Mode from Selected Vertices, Edges or Faces, or Curve Points. The Operator will work for different Context, including in Edit Mesh, Edit Curve, Edit Armature, Pose, and Object Mode. 

[CreateFromSelectedEditMeshIndividual.webm](https://user-images.githubusercontent.com/79613445/210190711-4b5e3c3d-5d7d-4f63-beb8-c63db8cc1034.webm)

[CreateFromSelectedObjectIndividual.webm](https://user-images.githubusercontent.com/79613445/210190714-01619bb2-1574-4f41-a9cb-1b5d61a8600b.webm)


### Generate Eyelid

Generate Eyelid set up in One Click

[GenerateEyelid.webm](https://user-images.githubusercontent.com/79613445/210190492-cd8abbb9-af27-4018-9ef2-258ba81e1f8a.webm)


### Generate Stretch Chain

Easily Generates Stretch Chain in just a few clicks, Useful if you use alot of Stretchy Bones

[GenerateStretchChain.webm](https://user-images.githubusercontent.com/79613445/210190228-583f6039-2567-48da-bae9-674c2130b26b.webm)

### Generate Twist Bone

Generate Twist Bone is a Quick Setup for Twist Bone especially for Forearm, this can use to prevent the "Candy Wrap Effects"

[GenerateTwistBone.webm](https://user-images.githubusercontent.com/79613445/210190555-b46a3c69-8223-4232-b634-78cb11bcaf02.webm)

# More Features & Documentation

Find Out More At [Bonera Documentation](https://boneradocumentation.readthedocs.io/en/latest/index.html)
