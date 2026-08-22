---
permalink: /
title: ""
excerpt: ""
description: "Inpyo Song is a Ph.D. student in computer vision and AI at SungKyunKwan University, working on object tracking, anomaly detection, human pose estimation, and traffic accident anticipation."
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

Hello! I'm Inpyo Song, a Ph.D. student researching computer vision and artificial intelligence, advised by [Prof. Jangwon Lee](https://leejang.github.io/).
My research focuses on video anomaly detection and real-world visual understanding. 
I study how visual systems can reliably recognize and understand unusual events in complex, open-ended environments, with particular interests in object-centric representations, vision-language models, and reliable evaluation.
My broader goal is to build vision systems that remain useful and trustworthy beyond controlled benchmark settings.
Also, I am honored to collaborate with [Prof. David Crandall](https://homes.luddy.indiana.edu/djcran/) from Indiana University Bloomington.

You can find my [CV](https://songinpyo.github.io/assets/InpyoSong_Curriculum_Vitae_Jun2026.pdf) here. 
I am always open to any form of collaboration. If you have any ideas for potential collaboration, or just feel like having a casual chat, please feel free to reach out!

<!-- <h3 id="research-interests">Research Interests</h3>
- Traffic Accident Anticipation -->



<!-- My research interest includes neural machine translation and computer vision. I have published more than 100 papers at the top international AI conferences with total <a href='https://scholar.google.com/citations?user=DhtAFkwAAAAJ'>google scholar citations <strong><span id='total_cit'>260000+</span></strong></a> (You can also use google scholar badge <a href='https://scholar.google.com/citations?user=DhtAFkwAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations"></a>). -->


# 🔥 News
- *Jun. 2026*: 🎉 "Bounding-Box Trajectories Matter for Video Anomaly Detection" accepted at ECCV 2026.
- *Jun. 2026*: 🏆 Received the Outstanding Poster Award at the KIBME Summer Conference 2026.
- *Aug. 2025*: 🏆 Received the Best Graduate Research Award at the 2025 Digital Innovation Talent Symposium.
- *May 2025*: 🎉 Two papers accepted at ICIP 2025.
- *Feb. 2025*: 🏆 Selected for I-Corps Korea Program.
- *Dec. 2024*: 🎉 One paper accepted at WACV 2025.
- *Oct. 2024*: 🎉 [SFTrack](https://songinpyo.github.io/SFTrack-Project/) presented as Long Oral Presentation at IROS 2024.
- *Oct. 2024*: 🏆 Received Excellence Award at SKKU Graduate Student Start-up Competition.
- *Sep. 2024*: 🎉 One paper accepted at CVIU.
- *Aug. 2024*: 🏆 Received President's Award from IITP at 2024 Digital Innovation Talent Symposium.
- *Jun. 2024*: Thrilled to join the Indiana University Bloomington CVLab as an intern!
- *Jun. 2024*: 🎉 One paper accepted at IROS 2024.

<h1 id="-publications">📝 Publications <span style="font-size: 0.5em; font-weight: normal;">(Selected)</span></h1>

{%- assign selected = site.publications | where: "selected", true | sort: "date" | reverse %}
<ol class="pub-list">
{%- for pub in selected %}
{%- include publication-item.html pub=pub %}
{%- endfor %}
</ol>

<p class="pub-more">
  <a href="/publications/" target="_self">See all {{ site.publications | size }} publications &rarr;</a>
</p>

# 🎖 Honors and Awards
- *Jun. 2026* Outstanding Poster Award, KIBME Summer Conference
- *Aug. 2025* Best Graduate Research Award, 2025 Digital Innovation Talent Symposium, Ministry of Science and ICT
- *Feb. 2025* Selected for I-Corps Korea Program (VLM-based Arduino Tutor)
- *Oct. 2024* Excellence Award, SKKU Graduate Student Startup Competition (Multimodal VQA-Based Tutoring System for the Digital Transformation of Hands-On Education)
- *Aug. 2024* President's Award from IITP, 2024 Digital Innovation Talent Symposium (Motion-Aware Heatmap Regression for Human Pose Estimation in Videos)
- *Feb. 2024* Encouragement Award, SKKU Research Matters (Technological Social Responsibility: Anomaly Detection for People with Visual Impairments Using an Egocentric 360-Degree Camera)
- *Dec. 2022* Grand Award from SKKU, KAU Start-up Idea Competition (Generating Digital Twin using Instance-NeRF)


<!-- # 📖 Educations
- *2019.06 - 2022.04 (now)*, Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus ornare aliquet ipsum, ac tempus justo dapibus sit amet.  -->

<!-- # 💬 Invited Talks
- *2021.06*, Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus ornare aliquet ipsum, ac tempus justo dapibus sit amet.  -->

# 💻 Internships
- *Jun. 2024 - Aug. 2024*, Research Intern @ [Indiana University Bloomington CVLab](http://vision.soic.indiana.edu), Bloomington, IN, USA

# 🤝 Professional Services

### Conference Reviewer
- AAAI 2027
- NeurIPS 2026
- CVPR 2026
- IROS 2026
- AAAI 2026
- WACV 2025
- ICDL 2024