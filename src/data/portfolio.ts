export interface SocialLink {
  label: string;
  url: string;
  handle: string;
  icon: "github" | "linkedin" | "email";
}

export interface PersonalInfo {
  name: string;
  tagline: string;
  location: string;
  bio: string[];
  imageUrl: string;
  socials: SocialLink[];
}

export interface Experience {
  company: string;
  position: string;
  location?: string;
  startDate: string;
  endDate: string;
  story: string;
  tags: string[];
  logo?: string;
}

export interface EducationItem {
  institution: string;
  degree: string;
  startDate: string;
  endDate: string;
  note: string;
  badges: string[];
  logo?: string;
}

export interface ProjectItem {
  title: string;
  kicker: string;
  story: string;
  stack: string[];
  link?: string;
}

export interface AwardItem {
  title: string;
  badge: string;
  year: string;
  blurb: string;
}

export const personalInfo: PersonalInfo = {
  name: "Nithika Dias",
  tagline: "Software & Application Security Engineer • Computer Science & Engineering Graduate",
  location: "Colombo, Sri Lanka",
  bio: [
    "I'm an Associate Engineer in Application Security at LSEG (London Stock Exchange Group) and a Computer Science & Engineering graduate from the University of Moratuwa, specializing in Cyber Security.",
    "Most of my work sits between application security testing with a little bit of software and cloud development as well. On the weekends, I try to keep up with all the new security research and tools in the space, mostly through Youtube and Articles.",
  ],
  imageUrl: "/profile-image.webp",
  socials: [
    {
      label: "GitHub",
      url: "https://github.com/psychlone77",
      handle: "psychlone77",
      icon: "github",
    },
    {
      label: "LinkedIn",
      url: "https://www.linkedin.com/in/nithika-dias/",
      handle: "nithika-dias",
      icon: "linkedin",
    },
    {
      label: "Email",
      url: "mailto:nithikasdias@gmail.com",
      handle: "nithikasdias@gmail.com",
      icon: "email",
    },
  ],
};

export const experiences: Experience[] = [
  {
    company: "LSEG (London Stock Exchange Group)",
    position: "Associate Engineer — Application Security",
    location: "Colombo, Sri Lanka",
    startDate: "2026",
    endDate: "Present",
    story:
      "Working on application security across LSEG's engineering teams—performing security reviews, identifying vulnerabilities early in the development lifecycle, and helping teams ship safer software.",
    tags: ["Application Security", "Cloud Security"],
    logo: "/logos/lseg.webp",
  },
  {
    company: "University of Moratuwa",
    position: "Teaching Assistant (Data Structures & Algorithms)",
    location: "Moratuwa, Sri Lanka",
    startDate: "Jan 2026",
    endDate: "June 2026",
    story:
      "Running weekly C++ lab sessions for first-year students. I help them work through core data structures, algorithm complexity, and debugging during their practical assignments.",
    tags: ["C++", "Data Structures", "Algorithms"],
    logo: "/logos/uom.webp",
  },
  {
    company: "Creative Software",
    position: "Software Engineer Intern",
    location: "Colombo, Sri Lanka",
    startDate: "Dec 2024",
    endDate: "July 2025",
    story:
      "Built a Dockerized technical drawing tool with React, Vite, and Python ML predictions to speed up manual drafting. Also developed a 3D structural visualization module in Three.js and React Three Fiber backed by .NET and MSSQL, and deployed container images to Azure with pluggable Azure SQL and MongoDB connectors.",
    tags: ["React", "Three.js", "Python", ".NET", "MSSQL", "Azure", "Docker"],
    logo: "/logos/creative-software.webp",
  },
  {
    company: "Upwork & Private Clients",
    position: "Freelance Software Engineer",
    location: "Remote",
    startDate: "2020",
    endDate: "2024",
    story:
      "Building and deploying web applications and high-performance landing pages for clients, handling LK Domain Registry and Netlify DNS configurations, and automating internal workflows using Google Apps Script.",
    tags: ["Next.js", "SEO", "DNS", "Google Apps Script"],
    logo: "/logos/upwork.webp",
  },
];

export const projects: ProjectItem[] = [
  {
    title: "Knob Tuner for Relational Databases",
    kicker: "Final Year Project • Ongoing",
    story:
      "Developing a lightweight machine learning pipeline in Python and PyTorch to automatically tune PostgreSQL configuration parameters based on workload characteristics, focusing on improving throughput and latency.",
    stack: ["PostgreSQL", "Python", "PyTorch"],
    link: "https://github.com/psychlone77/E2ETune-AI4DB",
  },
  {
    title: "Electronic Voting System",
    kicker: "Group Project",
    story:
      "Designed a verifiable e-voting protocol using Blind Signatures and Threshold Encryption to keep votes anonymous while allowing public auditability. Built with a NestJS server cluster, a React admin dashboard, and a React Native mobile app using Android Keystore and iOS Secure Enclave.",
    stack: ["Cryptography", "NestJS", "PostgreSQL", "React", "React Native"],
    link: "https://github.com/psychlone77/election-system-core",
  },
  {
    title: "OpenPapers",
    kicker: "Group Project",
    story:
      "A platform for Sri Lankan A/L students to find past papers and worked answers. Includes an OCR pipeline with a fine-tuned YOLOv12 model to extract questions and diagrams from scanned PDFs, rendered on Next.js with Markdown and LaTeX.",
    stack: ["Python", "YOLOv12", "Next.js", "NestJS", "MongoDB"],
    link: "https://github.com/psychlone77/openpapers-data-collecting",
  },
  {
    title: "Aquaculture Management System",
    kicker: "Solo Project",
    story:
      "Full-stack management system built with a React and Material UI frontend and a layered .NET backend (API, Business, and Data layers) backed by MSSQL on Azure.",
    stack: ["React", ".NET", "C#", "MSSQL", "Azure"],
    link: "https://github.com/psychlone77/FishFarmApp",
  },
  {
    title: "Airline Reservation System",
    kicker: "Group Project",
    story:
      "A flight scheduling and ticketing system where customers can book seats and admins manage flight operations. Worked across the Next.js frontend, backend routes, and custom MySQL schema design.",
    stack: ["Next.js", "Tailwind CSS", "MySQL", "SQL"],
    link: "https://github.com/psychlone77/b-airways-app",
  },
];

export const awards: AwardItem[] = [
  {
    title: "MoraXtreme 19 — Champion",
    badge: "1st Place",
    year: "2025",
    blurb:
      "Secured 1st place in the university-level competitive programming championship at the University of Moratuwa.",
  },
  {
    title: "IEEEXtreme 19.0",
    badge: "National 11th • Global 268th",
    year: "2025",
    blurb:
      "Ranked among the top teams globally in IEEE's 24-hour competitive programming competition.",
  },
  {
    title: "Bashaway Scripting Competition",
    badge: "Champion '24 • 2nd Runners Up '25",
    year: "2024 & 2025",
    blurb:
      "Won 1st place in 2024 and 2nd Runners Up in 2025 at the All-Island bash scripting competition organized by the SLIIT FOSS Community.",
  },
  {
    title: "Medusa 1.0 & 2.0 Inter-University CTF",
    badge: "Finalist",
    year: "2024 & 2025",
    blurb:
      "Reached the finals two years in a row at the Inter-University Capture The Flag competition hosted by the University of Kelaniya.",
  },
  {
    title: "CyberZee '24",
    badge: "Best Individual Performer",
    year: "2024",
    blurb:
      "Recognized for top individual performance across cybersecurity challenges, helping our team reach the finals.",
  },
];

export const education: EducationItem[] = [
  {
    institution: "University of Moratuwa",
    degree: "B.Sc. Engineering (Hons) in Computer Science & Engineering",
    startDate: "2022",
    endDate: "2026",
    note: "Graduated with First Class Honours specializing in Cyber Security. Also played on the University of Moratuwa basketball team (2021 – 2024).",
    badges: [
      "CGPA: 3.79 / 4.0 (First Class)",
      "Dean's List: Semesters 3, 5, 6, 7 & 8",
      "Specialization: Cyber Security",
    ],
    logo: "/logos/uom.webp",
  },
  {
    institution: "Lyceum International School, Nugegoda",
    degree: "G.C.E. A/L & G.C.S.E. O/L",
    startDate: "2007",
    endDate: "2020",
    note: "Served as Senior Prefect (2018 – 2019) and Deputy Athletic Captain (2018 – 2019).",
    badges: ["G.C.E. A/L 2020: 3 A's", "G.C.S.E. O/L 2018: 6 Distinctions"],
    logo: "/logos/lyceum.webp",
  },
];
