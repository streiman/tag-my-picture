[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<!-- <br /> -->
<!-- <p align="center"> -->
<!-- <a href="https://github.com/streiman/tag-my-picture"> -->
<!-- <img src="images/logo.png" alt="Logo" width="80" height="80"> -->
<!-- </a> -->

  <h3 align="center">tag-my-picture</h3>

  <p align="center">
    A python program that uses Amazon Rekognition and Amazon Translate (with boto3) to get labels for pictures and recognizes faces.
    <br />
    <a href="https://github.com/streiman/tag-my-picture"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    ·
    <a href="https://github.com/streiman/tag-my-picture/issues">Report Bug</a>
    ·
    <a href="https://github.com/streiman/tag-my-picture/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

I used to store my photos at Google Photos. But recently I switched to [PhotoPrism](https://github.com/photoprism/photoprism). It is under heavy development, but I missed two things at the moment:

* PhotoPrism adds labels to every picture like "sunset" or "tree", but they are only in English.
* PhotoPrism has no face recognition like Google Photos. But when i.e. I add a picture of my kids I want to get it automatically tagged with their names, so I can search for it.

Until PhotoPrism will add the features to the core program, I wrote a little program to add that functionality. It will of course work without PhotoPrism and with every picture library which reads exif date. The information I add to my pictures is stored in the keywords of the exif data. 

Tag-my-picture integrates in my workflow:

* Pictures I take are synchronized to a folder in my dropbox.
* A small bash script on my home server watches this folder for changes.
* When a new picture arrives, tag-my-picture is started.
* Afterwards it is moved to PhotoPrism using the WebDav access.

This is my first contribution to the Open Source Community and on GitHub, so probably I did some things wrong or could do better. Please feel free to contact me and give me some advice.

__Please take care! You should always keep a copy of your original pictures, because tag-my-picture changes the exif data. If something weird happens, you don't want to lose your pictures.__

__At the moment, tag-my-pictures is probably only useful to people, who can code in Python. It is not user friendly or working from the shell.__

### Built With

* [AWS SDK for Python (Boto3)](https://aws.amazon.com/de/sdk-for-python/)

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

* You have to setup AWS Rekognition. Please follow [the steps in the AWS documentation](https://docs.aws.amazon.com/rekognition/latest/dg/getting-started.html). Be aware that AWS Rekognition is not for free. You can get a free trial period, but please read [the AWS documents carefully](https://aws.amazon.com/de/rekognition/pricing/). AWS Translate is [also not for free](https://aws.amazon.com/de/translate/pricing/). 
* You need to install two python libraries:
  ```
  pip3 install boto3
  pip3 install pillow
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/streiman/tag-my-picture.git
   ```
2. Change the variables in tag-my-pictures.py according to your paths. 

<!-- USAGE EXAMPLES -->
## Usage

You need to create two folders:

1. One to store the faces of the people you know and want to recognize. You could for example use the folder /home/me/faces. In this folder you create subfolders for every person, for example 
* Peter
* Paul
* Mary

2. A folder where faces of unknown persons are copied, like /home/me/_unknown. You can use them to create new persons in your /home/me/faces-folder or you can delete them, if they are not important to you.

And you have to tell tag-my-pictures where the pictures are stored you want to process. If you run tag-my-pictures, all files in this folder will be read, one by one. If it is a picture like jpg, it will be processed.

First AWS Rekognition will be asked for labels for this picutre. The retrieved labels are then translated to German (you could change the language in the code). Because labels are recurring in many pictures, the translation is also saved in a local file. If an English label is found there, it will be used. Otherwise Amazon Translate is asked for the translation. You can also edit this file to get better translations.

If the picture has a label "person" or "human", the picture is afterwards sent to face detection. First all faces on the picture are cropped and saved in temporary files. Then they are queried against all the faces you stored in your /home/me/faces-folder, which is stored as a so called collection at AWS Rekognition and updated at the start of the program. So you can add new people by just creating subfolders and adding pictures, everything else happens in the background. 

If a face is recognized, the name of the person (the name of the subfolder where the picture is stored) is saved in the exif keywords.

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/streiman/tag-my-picture/issues) for a list of proposed features (and known issues).

I will try to make tag-my-picture more userfriendly.

I will also try to use different services for

* labelling
* translation
* face recognition

<!-- CONTRIBUTING -->
## Contributing

Feel free to make tag-my-picture better and useful for you. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE 
## License

Distributed under the MIT License. See `LICENSE` for more information. -->

<!-- CONTACT -->
## Contact

Andreas - [@astreim](https://twitter.com/astreim) - webmail@streim.de

Project Link: [https://github.com/streiman/tag-my-picture](https://github.com/streiman/tag-my-picture)

<!-- ACKNOWLEDGEMENTS 
## Acknowledgements

* []()
* []()
* []() -->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/streiman/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/streiman/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/streiman/repo.svg?style=for-the-badge
[forks-url]: https://github.com/streiman/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/streiman/repo.svg?style=for-the-badge
[stars-url]: https://github.com/streiman/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/streiman/repo.svg?style=for-the-badge
[issues-url]: https://github.com/streiman/repo/issues
[license-shield]: https://img.shields.io/github/license/streiman/repo.svg?style=for-the-badge
[license-url]: https://github.com/streiman/repo/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/streiman
