
"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Bot,
  BrainCircuit,
  BriefcaseBusiness,
  Check,
  Code2,
  Database,
  GraduationCap,
  House,
  Mail,
  Menu,
  MessageCircle,
  Send,
  Sparkles,
  Terminal,
  UserRound,
  X,
  Zap,
} from "lucide-react";

const EMAIL = "ojaswaoffice@gmail.com";
const WHATSAPP = "https://wa.me/916265877545";
const GITHUB = "https://github.com/ojaswa-1208";
const INSTAGRAM = "https://www.instagram.com/ojaswaai/";

const CHAT_API_URL =
  process.env.NEXT_PUBLIC_CHAT_API_URL ||
  "http://localhost:8000/api/v1/chat";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const INITIAL_MESSAGE =
  "Hello! I'm Ojaswa's AI portfolio assistant. Ask me about his projects, technical skills, education, or AI engineering journey.";

const MAX_HISTORY_MESSAGES = 8;
const MAX_HISTORY_CONTENT_LENGTH = 2000;

function normalizeChatMarkdown(content: string) {
  return content
    .replace(/\\\|/g, "|")
    .replace(/\\<br\s*\/?>/gi, "\n")
    .replace(/&lt;br\s*\/?&gt;/gi, "\n");
}

function buildSafeHistory(messages: ChatMessage[]) {
  return messages
    .filter(
      (item) =>
        (item.role === "user" || item.role === "assistant") &&
        typeof item.content === "string"
    )
    .map((item) => ({
      role: item.role,
      content: item.content.trim().slice(0, MAX_HISTORY_CONTENT_LENGTH),
    }))
    .filter((item) => item.content.length > 0)
    .slice(-MAX_HISTORY_MESSAGES);
}

function InstagramIcon({ size = 18 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

const navigation = [
  { label: "Home", href: "#home", icon: House },
  { label: "About", href: "#about", icon: UserRound },
  { label: "Skills", href: "#skills", icon: Code2 },
  { label: "Projects", href: "#projects", icon: BriefcaseBusiness },
  { label: "Education", href: "#education", icon: GraduationCap },
  { label: "Contact", href: "#contact", icon: Mail },
];

const skillGroups = [
  {
    title: "AI & Machine Learning",
    description: "Building predictive and explainable systems.",
    icon: BrainCircuit,
    skills: ["Python", "Scikit-learn", "Machine Learning", "SHAP", "Pandas", "NumPy"],
  },
  {
    title: "LLMs & Agentic AI",
    description: "Exploring intelligent retrieval and AI applications.",
    icon: Sparkles,
    skills: ["LLMs", "RAG", "Qdrant", "ChromaDB", "Sentence Transformers", "AI Agents"],
  },
  {
    title: "Backend Engineering",
    description: "Connecting models to real-world applications.",
    icon: Terminal,
    skills: ["FastAPI", "REST APIs", "SQL", "Git", "Python"],
  },
  {
    title: "Data & Analytics",
    description: "Turning raw data into useful insights.",
    icon: Database,
    skills: ["MySQL", "Power BI", "Data Cleaning", "Feature Engineering"],
  },
];

const projects = [
  {
    number: "01",
    title: "AI Portfolio Assistant",
    category: "LLM APPLICATION · RAG",
    description:
      "An AI-powered portfolio assistant that uses retrieval-augmented generation to answer questions about my background, technical skills, and projects.",
    technologies: ["FastAPI", "Groq", "Qdrant", "Sentence Transformers", "Next.js"],
    icon: Bot,
    status: "In development",
    github: GITHUB,
  },
  {
    number: "02",
    title: "AI Retention Diagnosis",
    category: "MACHINE LEARNING · EXPLAINABLE AI",
    description:
      "A customer churn analysis application combining machine learning, SHAP-based explanations, and retrieval-assisted retention recommendations.",
    technologies: ["Python", "Scikit-learn", "SHAP", "Streamlit", "ChromaDB"],
    icon: BrainCircuit,
    status: "Built",
    github: "https://github.com/ojaswa-1208/ai-retention-diagnosis",
    demo: "https://ai-retention-diagnosis-pbizgwpuphgi6c4ffpderd.streamlit.app",
  },
  {
    number: "03",
    title: "Retail Customer Segmentation",
    category: "DATA ANALYTICS · BUSINESS INTELLIGENCE",
    description:
      "A customer analytics project using data preparation, feature engineering, segmentation, and interactive Power BI reporting.",
    technologies: ["Python", "Pandas", "NumPy", "MySQL", "Power BI"],
    icon: Database,
    status: "Built",
    github: GITHUB,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  visible: { opacity: 1, y: 0 },
};

export default function Home() {
  const [activeSection, setActiveSection] = useState("Home");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: INITIAL_MESSAGE },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sections = navigation
      .map((item) => document.querySelector(item.href))
      .filter((section): section is Element => section !== null);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort(
            (a, b) =>
              b.intersectionRatio - a.intersectionRatio
          );

        if (visible[0]) {
          const section = visible[0].target.id;
          const match = navigation.find(
            (item) => item.href === `#${section}`
          );

          if (match) setActiveSection(match.label);
        }
      },
      { rootMargin: "-20% 0px -65% 0px", threshold: [0, 0.2, 0.5] }
    );

    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [chatMessages, chatLoading]);

  const navigate = (label: string) => {
    setActiveSection(label);
    setMobileMenuOpen(false);
  };

  const startNewChat = () => {
    if (chatLoading) return;

    setChatMessages([{ role: "assistant", content: INITIAL_MESSAGE }]);
    setChatInput("");
    setChatError("");
  };

  const sendChatMessage = async () => {
    const message = chatInput.trim();

    if (!message || chatLoading) return;

    const history = buildSafeHistory(chatMessages);

    setChatMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);

    setChatInput("");
    setChatError("");
    setChatLoading(true);

    try {
      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 422) {
          let validationMessage =
            "The message could not be validated. Please try again.";

          if (Array.isArray(data?.detail)) {
            validationMessage = data.detail
              .map((error: { loc?: unknown[]; msg?: string }) => {
                const field = Array.isArray(error.loc)
                  ? error.loc.join(".")
                  : "Request";
                return `${field}: ${error.msg || "Invalid value"}`;
              })
              .join(" | ");
          } else if (typeof data?.detail === "string") {
            validationMessage = data.detail;
          }

          throw new Error(validationMessage);
        }

        if (response.status === 429) {
          throw new Error(
            "Too many requests. Please wait a minute before trying again."
          );
        }

        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : `The assistant could not process your request. Status: ${response.status}`
        );
      }

      if (typeof data?.answer !== "string" || !data.answer.trim()) {
        throw new Error("The AI returned an empty response.");
      }

      setChatMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.answer.trim() },
      ]);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Something went wrong.";

      setChatError(errorMessage);

      setChatMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't respond right now. Please check that the portfolio backend is running and try again.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="clean-shell">
      {/* MOBILE NAVIGATION OVERLAY */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.button
            className="clean-mobile-overlay"
            aria-label="Close navigation"
            onClick={() => setMobileMenuOpen(false)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </AnimatePresence>

      {/* SIDEBAR */}
      <aside className={`clean-sidebar ${mobileMenuOpen ? "is-open" : ""}`}>
        <div className="clean-brand">
          <a href="#home" className="clean-brand-mark" onClick={() => navigate("Home")}>
            O.
          </a>
          <div>
            <strong>OJASWA MAHOBIYA</strong>
            <span>PERSONAL PORTFOLIO</span>
          </div>
          <button
            className="clean-mobile-close"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation"
          >
            <X size={19} />
          </button>
        </div>

        <div className="clean-profile">
          <div className="clean-avatar">OM</div>
          <strong>Ojaswa Mahobiya</strong>
          <span>AI ENGINEER · STUDENT</span>
        </div>

        <div className="clean-nav-label">NAVIGATION</div>

        <nav className="clean-nav">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <a
                key={item.label}
                href={item.href}
                onClick={() => navigate(item.label)}
                className={activeSection === item.label ? "active" : ""}
              >
                <Icon size={17} strokeWidth={1.8} />
                <span>{item.label}</span>
                {activeSection === item.label && <span className="clean-nav-dot" />}
              </a>
            );
          })}
        </nav>

        <div className="clean-sidebar-bottom">
          <div className="clean-open-status">
            <span />
            Open to opportunities
          </div>

          <div className="clean-social-links">
            <a href={GITHUB} target="_blank" rel="noreferrer" aria-label="GitHub">
              <Code2 size={18} />
            </a>
            <a href={`mailto:${EMAIL}`} aria-label="Email">
              <Mail size={18} />
            </a>
            <a href={WHATSAPP} target="_blank" rel="noreferrer" aria-label="WhatsApp">
              <MessageCircle size={18} />
            </a>
            <a href={INSTAGRAM} target="_blank" rel="noreferrer" aria-label="Instagram">
              <InstagramIcon size={18} />
            </a>
          </div>

          <span className="clean-copyright">© 2026 Ojaswa Mahobiya</span>
        </div>
      </aside>

      {/* MAIN */}
      <div className="clean-main">
        <header className="clean-topbar">
          <button
            className="clean-menu-button"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>

          <div className="clean-breadcrumb">
            Portfolio <span>/</span> <strong>{activeSection}</strong>
          </div>

          <div className="clean-topbar-right">
            <span className="clean-online">
              <span /> Available for opportunities
            </span>
            <a href={`mailto:${EMAIL}`} className="clean-topbar-link">
              Contact <ArrowUpRight size={15} />
            </a>
          </div>
        </header>

        <div className="clean-content">
          {/* HERO */}
          <section id="home" className="clean-hero">
            <motion.div
              className="clean-hero-copy"
              initial="hidden"
              animate="visible"
              variants={{
                visible: { transition: { staggerChildren: 0.12 } },
              }}
            >
              <motion.div variants={fadeUp} className="clean-eyebrow">
                <span /> HELLO, I'M
              </motion.div>

              <motion.h1 variants={fadeUp}>
                Ojaswa
                <br />
                <span>Mahobiya.</span>
              </motion.h1>

              <motion.div variants={fadeUp} className="clean-hero-role">
                AI Engineer <span>·</span> Agentic AI Developer
              </motion.div>

              <motion.p variants={fadeUp} className="clean-hero-description">
                I build intelligent applications using Python, LLMs, and
                retrieval-augmented generation. Interested in turning
                emerging AI technologies into practical solutions.
              </motion.p>

              <motion.div variants={fadeUp} className="clean-hero-actions">
                <a href="#projects" className="clean-button-primary">
                  Explore my work <ArrowUpRight size={17} />
                </a>
                <a href="#contact" className="clean-button-secondary">
                  Get in touch <ArrowRight size={16} />
                </a>
              </motion.div>

              <motion.div variants={fadeUp} className="clean-hero-socials">
                <span>FIND ME</span>
                <a href={GITHUB} target="_blank" rel="noreferrer">
                  <Code2 size={16} /> GitHub
                </a>
                <a href={`mailto:${EMAIL}`}>
                  <Mail size={16} /> Email
                </a>
                <a href={INSTAGRAM} target="_blank" rel="noreferrer">
                  <InstagramIcon size={16} /> Instagram
                </a>
              </motion.div>
            </motion.div>

            <motion.div
              className="clean-hero-art"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
            >
              <div className="clean-art-top">
                <span>EXPLORING THE WORLD OF</span>
                <span>01 — 03</span>
              </div>

              <div className="clean-art-symbol">
                <BrainCircuit size={112} strokeWidth={0.85} />
              </div>

              <div className="clean-art-bottom">
                <div>
                  <strong>Artificial Intelligence</strong>
                  <span>Building with curiosity and purpose.</span>
                </div>
                <Sparkles size={23} />
              </div>

              <div className="clean-art-orb clean-orb-one" />
              <div className="clean-art-orb clean-orb-two" />
            </motion.div>

            <a href="#about" className="clean-scroll-note">
              SCROLL TO EXPLORE <ArrowDown size={15} />
            </a>
          </section>

          {/* QUICK FACTS */}
          <section className="clean-facts">
            <div>
              <span>01</span>
              <strong>AI & ML</strong>
              <small>PRIMARY FOCUS</small>
            </div>
            <div>
              <span>02</span>
              <strong>LLMs & RAG</strong>
              <small>BUILDING WITH</small>
            </div>
            <div>
              <span>03</span>
              <strong>Projects</strong>
              <small>HANDS-ON LEARNING</small>
            </div>
            <div>
              <span>04</span>
              <strong>Always learning</strong>
              <small>PERSONAL APPROACH</small>
            </div>
          </section>

          {/* ABOUT */}
          <section id="about" className="clean-section">
            <div className="clean-section-heading">
              <div>
                <span>01 / ABOUT</span>
                <h2>Curiosity into <em>creation.</em></h2>
              </div>
              <small>A LITTLE ABOUT ME</small>
            </div>

            <div className="clean-about-grid">
              <div>
                <p className="clean-about-lead">
                  I'm an AI/ML engineering student interested in building
                  useful, intelligent applications.
                </p>
                <p className="clean-body-copy">
                  My journey focuses on understanding how AI systems work
                  beyond model training — from data and embeddings to
                  retrieval, APIs, and real-world application development.
                </p>
                <p className="clean-body-copy">
                  I'm currently exploring LLM applications, RAG
                  architectures, and Agentic AI while strengthening my
                  foundations in software engineering.
                </p>
              </div>

              <div className="clean-about-aside">
                <span className="clean-aside-label">CURRENT INTERESTS</span>
                <div><BrainCircuit size={19} /> Agentic AI</div>
                <div><Database size={19} /> Retrieval systems</div>
                <div><Zap size={19} /> AI Engineering</div>
                <div className="clean-location">BASED IN BHOPAL, INDIA</div>
              </div>
            </div>
          </section>

          {/* SKILLS */}
          <section id="skills" className="clean-section">
            <div className="clean-section-heading">
              <div>
                <span>02 / TECHNICAL SKILLS</span>
                <h2>Tools of my <em>trade.</em></h2>
              </div>
              <small>MY TOOLKIT</small>
            </div>

            <div className="clean-skills-grid">
              {skillGroups.map((group, index) => {
                const Icon = group.icon;

                return (
                  <motion.article
                    key={group.title}
                    className="clean-skill-card"
                    initial={{ opacity: 0, y: 18 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.07 }}
                  >
                    <div className="clean-skill-card-head">
                      <div className="clean-skill-icon"><Icon size={21} /></div>
                      <span>0{index + 1}</span>
                    </div>
                    <h3>{group.title}</h3>
                    <p>{group.description}</p>
                    <div className="clean-skill-tags">
                      {group.skills.map((skill) => (
                        <span key={skill}>{skill}</span>
                      ))}
                    </div>
                  </motion.article>
                );
              })}
            </div>
          </section>

          {/* PROJECTS */}
          <section id="projects" className="clean-section">
            <div className="clean-section-heading">
              <div>
                <span>03 / SELECTED WORK</span>
                <h2>Projects with <em>purpose.</em></h2>
              </div>
              <a href={GITHUB} target="_blank" rel="noreferrer" className="clean-view-all">
                View GitHub <ArrowUpRight size={16} />
              </a>
            </div>

            <div className="clean-projects">
              {projects.map((project, index) => {
                const Icon = project.icon;

                return (
                  <motion.article
                    key={project.number}
                    className="clean-project-card"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.08 }}
                  >
                    <div className="clean-project-number">{project.number}</div>

                    <div className="clean-project-icon"><Icon size={26} /></div>

                    <div className="clean-project-main">
                      <span>{project.category}</span>
                      <h3>{project.title}</h3>
                      <p>{project.description}</p>
                      <div className="clean-project-tags">
                        {project.technologies.map((tech) => (
                          <span key={tech}>{tech}</span>
                        ))}
                      </div>
                    </div>

                    <div className="clean-project-actions">
                      <span className={project.status === "Built" ? "built" : ""}>
                        <i /> {project.status}
                      </span>
                      <div>
                        <a
                          href={project.github}
                          target="_blank"
                          rel="noreferrer"
                          aria-label={`GitHub repository for ${project.title}`}
                        >
                          <Code2 size={19} />
                        </a>
                        {project.demo && (
                          <a
                            href={project.demo}
                            target="_blank"
                            rel="noreferrer"
                            aria-label={`Live demo for ${project.title}`}
                          >
                            <ArrowUpRight size={19} />
                          </a>
                        )}
                      </div>
                    </div>
                  </motion.article>
                );
              })}
            </div>
          </section>

          {/* EDUCATION */}
          <section id="education" className="clean-section">
            <div className="clean-section-heading">
              <div>
                <span>04 / EDUCATION</span>
                <h2>Where it <em>began.</em></h2>
              </div>
              <small>LEARNING JOURNEY</small>
            </div>

            <article className="clean-education-card">
              <div className="clean-education-icon">
                <GraduationCap size={27} />
              </div>
              <div>
                <span>UNDERGRADUATE DEGREE</span>
                <h3>B.Tech — Computer Science & Engineering</h3>
                <p>Artificial Intelligence & Machine Learning</p>
                <small>SISTec Ratibad · Bhopal, Madhya Pradesh</small>
              </div>
              <div className="clean-education-status">
                <Check size={14} /> Currently studying
              </div>
            </article>
          </section>

          {/* CONTACT */}
          <section id="contact" className="clean-contact">
            <span>05 / CONTACT</span>
            <h2>
              Let's make something
              <br />
              <em>meaningful.</em>
            </h2>
            <p>
              Have an idea, an opportunity, or an interesting AI problem?
              I'd be happy to connect.
            </p>

            <div className="clean-contact-actions">
              <a
                href={`mailto:${EMAIL}`}
                className="clean-button-primary"
              >
                Email me <Mail size={17} />
              </a>
              <a
                href={WHATSAPP}
                target="_blank"
                rel="noreferrer"
                className="clean-button-secondary"
              >
                WhatsApp <MessageCircle size={17} />
              </a>
              <a
                href={INSTAGRAM}
                target="_blank"
                rel="noreferrer"
                className="clean-button-secondary"
              >
                Instagram <InstagramIcon size={17} />
                <ArrowUpRight size={15} />
              </a>
            </div>

            <div className="clean-contact-footer">
              <span>DESIGNED & BUILT BY OJASWA MAHOBIYA</span>
              <span>BHOPAL, INDIA · 2026</span>
            </div>
          </section>
        </div>
      </div>

      {/* CHAT LAUNCHER */}
      <button
        className="clean-chat-launcher"
        onClick={() => setChatOpen((open) => !open)}
        aria-label={chatOpen ? "Close AI assistant" : "Open AI assistant"}
      >
        {chatOpen ? <X size={22} /> : <MessageCircle size={22} />}
        {!chatOpen && <span />}
      </button>

      {/* CHAT PANEL */}
      <AnimatePresence>
        {chatOpen && (
          <motion.section
            className="clean-chat-panel"
            initial={{ opacity: 0, y: 18, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 18, scale: 0.97 }}
            transition={{ duration: 0.2 }}
            aria-label="Ojaswa AI portfolio assistant"
          >
            <header className="clean-chat-header">
              <div className="clean-chat-avatar"><Bot size={21} /></div>
              <div>
                <strong>Ojaswa's AI Assistant</strong>
                <span><i /> Portfolio knowledge assistant</span>
              </div>
              <button
                type="button"
                className="clean-chat-new"
                onClick={startNewChat}
                disabled={chatLoading}
              >
                New chat
              </button>
              <button
                type="button"
                className="clean-chat-close"
                onClick={() => setChatOpen(false)}
                aria-label="Close assistant"
              >
                <X size={18} />
              </button>
            </header>

            <div className="clean-chat-messages" aria-live="polite">
              {chatMessages.map((message, index) => (
                <div
                  key={`${index}-${message.role}`}
                  className={`clean-chat-row ${message.role}`}
                >
                  {message.role === "assistant" && (
                    <div className="clean-chat-message-avatar">
                      <Bot size={15} />
                    </div>
                  )}

                  <div className="clean-chat-bubble">
                    <div className="clean-chat-markdown">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          a: ({ ...props }) => (
                            <a
                              {...props}
                              target="_blank"
                              rel="noopener noreferrer"
                            />
                          ),
                        }}
                      >
                        {normalizeChatMarkdown(message.content)}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))}

              {chatLoading && (
                <div className="clean-chat-row assistant">
                  <div className="clean-chat-message-avatar">
                    <Bot size={15} />
                  </div>
                  <div className="clean-chat-bubble">
                    <div className="clean-chat-typing">
                      <span /><span /><span />
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {chatError && (
              <p className="clean-chat-error" role="alert">{chatError}</p>
            )}

            <form
              className="clean-chat-input"
              onSubmit={(event) => {
                event.preventDefault();
                void sendChatMessage();
              }}
            >
              <input
                type="text"
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                placeholder="Ask about projects, skills..."
                maxLength={2000}
                disabled={chatLoading}
                aria-label="Message the AI assistant"
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || chatLoading}
                aria-label="Send message"
              >
                <Send size={17} />
              </button>
            </form>

            <div className="clean-chat-footnote">
              <span><Sparkles size={12} /> AI-powered portfolio assistant</span>
              <span>Responses may need verification</span>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </main>
  );
}
