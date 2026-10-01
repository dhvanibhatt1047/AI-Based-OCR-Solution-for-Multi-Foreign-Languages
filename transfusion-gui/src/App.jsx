import { useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowUp,
  Bot,
  Check,
  ChevronRight,
  Clock3,
  Copy,
  Database,
  Download,
  FileText,
  Image as ImageIcon,
  Languages,
  Menu,
  MessageSquarePlus,
  Paperclip,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Zap,
} from "lucide-react";
import "./App.css";

const demoChats = [
  {
    id: 1,
    title: "Chinese product description",
    preview: "你好，欢迎使用我们的产品...",
    time: "Today",
    type: "text",
  },
  {
    id: 2,
    title: "Chinese document translation",
    preview: "技术说明与产品规格...",
    time: "Today",
    type: "document",
  },
  {
    id: 3,
    title: "Image translation",
    preview: "图片中的中文内容...",
    time: "Yesterday",
    type: "image",
  },
];

const demoOriginal = `你好，欢迎使用我们的多语言翻译系统。
该系统可以从图像和文档中提取中文文本，并根据上下文进行准确翻译。`;

const demoTranslation = `Hello, welcome to our multilingual translation system.
The system can extract Chinese text from images and documents and provide accurate translations based on context.`;

function App() {
  const fileInputRef = useRef(null);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [history, setHistory] = useState(demoChats);
  const [activeHistory, setActiveHistory] = useState(null);

  const [inputText, setInputText] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [language, setLanguage] = useState("Chinese → English");
  const [dragging, setDragging] = useState(false);

  const [isProcessing, setIsProcessing] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [saveDecision, setSaveDecision] = useState(null);
  const [databaseStatus, setDatabaseStatus] = useState("Database lookup pending");

  const [accuracy, setAccuracy] = useState(94.6);
  const [confidence, setConfidence] = useState(92.8);

  const [translationResult, setTranslationResult] = useState("");
  const [chineseResult, setChineseResult] = useState("");

  const hasInput = inputText.trim() || selectedFiles.length > 0;

  const createNewChat = () => {
    setInputText("");
    setSelectedFiles([]);
    setShowResult(false);
    setSaveDecision(null);
    setActiveHistory(null);
    setDatabaseStatus("Database lookup pending");
  };

  const addFiles = (fileList) => {
    const validFiles = Array.from(fileList).filter((file) =>
      [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
      ].includes(file.type)
    );

    setSelectedFiles((previous) =>
      [...previous, ...validFiles].slice(0, 5)
    );

    setShowResult(false);
    setSaveDecision(null);
  };

  const removeFile = (index) => {
    setSelectedFiles((previous) =>
      previous.filter((_, fileIndex) => fileIndex !== index)
    );
  };

  const simulateTranslation = async () => {
  if (!hasInput) return;

  setIsProcessing(true);
  setShowResult(false);
  setSaveDecision(null);
  setDatabaseStatus("Sending to backend...");

  try {
    let response;

    if (selectedFiles.length > 0) {
      const formData = new FormData();
      formData.append("file", selectedFiles[0]);

      setDatabaseStatus("Running OCR and translation...");
      response = await fetch("http://localhost:8000/translate", {
        method: "POST",
        body: formData,
      });
    } else {
      setDatabaseStatus("Translating text...");
      response = await fetch("http://localhost:8000/translate-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, direction: language }),
      });
    }

    if (!response.ok) throw new Error("Request failed");

    const data = await response.json();

    setChineseResult(data.chinese_text);
    setTranslationResult(data.english_text);
    setAccuracy(data.accuracy);
    setConfidence(data.confidence);
    setDatabaseStatus("Verification completed");
    setIsProcessing(false);
    setShowResult(true);

    const title =
      inputText.trim().slice(0, 35) ||
      selectedFiles[0]?.name ||
      "New translation";

    const newHistory = {
      id: Date.now(),
      title,
      preview:
        inputText.trim().slice(0, 55) ||
        selectedFiles.map((file) => file.name).join(", "),
      time: "Just now",
      type: selectedFiles.length
        ? selectedFiles[0].type.includes("pdf")
          ? "document"
          : "image"
        : "text",
    };

    setHistory((previous) => [
      newHistory,
      ...previous.filter((item) => item.id !== newHistory.id),
    ]);

    setActiveHistory(newHistory.id);
  } catch (error) {
    console.error(error);
    setDatabaseStatus("Error: could not reach backend");
    setIsProcessing(false);
  }
};

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      simulateTranslation();
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    addFiles(event.dataTransfer.files);
  };

  const selectHistory = (chat) => {
    setActiveHistory(chat.id);

    setInputText(
      chat.type === "text"
        ? demoOriginal
        : ""
    );

    setSelectedFiles([]);
    setShowResult(true);
    setSaveDecision(null);
    setDatabaseStatus("Translation retrieved from history");
  };

  const saveToDatabase = () => {
    setSaveDecision("saved");
    setDatabaseStatus("Translation approved for reusable database");
  };

  const keepPrivate = () => {
    setSaveDecision("private");
    setDatabaseStatus("Translation kept private");
  };

  const copyTranslation = async () => {
    try {
      await navigator.clipboard.writeText(translationResult);
    } catch {
      // Clipboard access can be blocked by the browser.
    }
  };

  const downloadTranslation = () => {
    const blob = new Blob([translationResult], {
      type: "text/plain;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = "transfusion-translation.txt";
    anchor.click();

    URL.revokeObjectURL(url);
  };

  const inputPreview =
    inputText.trim() ||
    (selectedFiles.length
      ? `Uploaded: ${selectedFiles.map((file) => file.name).join(", ")}`
      : "Your Chinese input will appear here.");

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">
            <Sparkles size={19} />
          </div>

          {sidebarOpen && (
            <div className="brand-copy">
              <strong>
                TransFusion<span>_AI</span>
              </strong>
              <small>Multilingual intelligence</small>
            </div>
          )}

          {sidebarOpen && (
            <button
              className="icon-button sidebar-toggle"
              onClick={() => setSidebarOpen(false)}
              aria-label="Collapse sidebar"
            >
              <Menu size={19} />
            </button>
          )}
        </div>

        {!sidebarOpen && (
          <button
            className="sidebar-expand"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu size={20} />
          </button>
        )}

        {sidebarOpen && (
          <button className="new-chat" onClick={createNewChat}>
            <MessageSquarePlus size={18} />
            <span>New translation</span>
            <kbd>Ctrl K</kbd>
          </button>
        )}

        {sidebarOpen && (
          <div className="history-heading">
            <span>Translation history</span>
            <Clock3 size={14} />
          </div>
        )}

        <div className="history-list">
          {sidebarOpen &&
            history.map((chat) => (
              <button
                key={chat.id}
                className={`history-item ${activeHistory === chat.id ? "active" : ""
                  }`}
                onClick={() => selectHistory(chat)}
              >
                <div className="history-icon">
                  {chat.type === "image" ? (
                    <ImageIcon size={16} />
                  ) : chat.type === "document" ? (
                    <FileText size={16} />
                  ) : (
                    <Languages size={16} />
                  )}
                </div>

                <div className="history-content">
                  <strong>{chat.title}</strong>
                  <span>{chat.preview}</span>
                  <small>{chat.time}</small>
                </div>

                <ChevronRight size={15} className="history-arrow" />
              </button>
            ))}
        </div>

        {sidebarOpen && (
          <div className="sidebar-footer">
            <div className="privacy-mini">
              <ShieldCheck size={17} />
              <div>
                <strong>Privacy controlled</strong>
                <span>You decide what enters the reusable corpus.</span>
              </div>
            </div>

            <div className="version-label">
              TransFusion AI · Translation Workspace
            </div>
          </div>
        )}
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu"
              onClick={() => setSidebarOpen((value) => !value)}
            >
              <Menu size={20} />
            </button>

            <div>
              <span className="topbar-label">Translation workspace</span>
              <strong>Chinese → English</strong>
            </div>
          </div>

          <div className="topbar-status">
            <span className="online-dot" />
            System ready
          </div>
        </header>

        <section className="workspace">
          <div className="workspace-header">
            <div>
              <div className="eyebrow">
                <span />
                AI-powered multilingual translation
              </div>

              <h1>
                Translate with <em>context.</em>
              </h1>

              <p>
                Upload a document, image, or enter Chinese text. TransFusion AI
                processes meaningful blocks, checks reusable translations, and
                verifies the result.
              </p>
            </div>

            <div className="architecture-pill">
              <Zap size={16} />
              Context-aware pipeline
            </div>
          </div>

          <div className="translation-workspace">
            <section className="input-card panel">
              <div className="panel-header">
                <div>
                  <span className="panel-kicker">01 · INPUT</span>
                  <h2>Original content</h2>
                </div>

                <div className="format-badge">
                  {selectedFiles.length ? "FILE" : "TEXT"}
                </div>
              </div>

              <div
                className={`input-area ${dragging ? "drag-active" : ""}`}
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
              >
                {selectedFiles.length > 0 && (
                  <div className="file-list">
                    {selectedFiles.map((file, index) => (
                      <div className="file-chip" key={`${file.name}-${index}`}>
                        {file.type === "application/pdf" ? (
                          <FileText size={15} />
                        ) : (
                          <ImageIcon size={15} />
                        )}

                        <span>{file.name}</span>

                        <button
                          onClick={() => removeFile(index)}
                          aria-label={`Remove ${file.name}`}
                        >
                          <X size={13} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <textarea
                  value={inputText}
                  onChange={(event) => {
                    setInputText(event.target.value);
                    setShowResult(false);
                    setSaveDecision(null);
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="在这里输入中文文本..."
                />

                {!inputText && selectedFiles.length === 0 && (
                  <div className="drop-hint">
                    <div className="drop-icon">
                      <Upload size={20} />
                    </div>

                    <strong>Drop a Chinese document or image here</strong>

                    <span>
                      PDF, PNG, JPG, WEBP or type Chinese text directly
                    </span>
                  </div>
                )}
              </div>

              <div className="input-actions">
                <button
                  className="secondary-button"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Paperclip size={16} />
                  Attach file
                </button>

                <input
                  ref={fileInputRef}
                  hidden
                  multiple
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.webp"
                  onChange={(event) => addFiles(event.target.files)}
                />

                <div className="language-control">
                  <Languages size={15} />

                  <select
                    value={language}
                    onChange={(event) => setLanguage(event.target.value)}
                  >
                    <option>Chinese → English</option>
                    <option>English → Chinese</option>
                    <option>Auto detect</option>
                  </select>
                </div>

                <button
                  className={`translate-button ${hasInput ? "ready" : ""
                    }`}
                  onClick={simulateTranslation}
                  disabled={!hasInput || isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <span className="spinner" />
                      Processing
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} />
                      Translate
                    </>
                  )}
                </button>
              </div>

              <div className="input-note">
                <ShieldCheck size={14} />
                Your translation is not added to the reusable database unless
                you explicitly approve it.
              </div>
            </section>

            <section className="result-card panel">
              <div className="panel-header">
                <div>
                  <span className="panel-kicker">02 · OUTPUT</span>
                  <h2>English translation</h2>
                </div>

                <div className="verified-badge">
                  <Check size={14} />
                  Verified
                </div>
              </div>

              {isProcessing ? (
                <div className="processing-state">
                  <div className="processing-orbit">
                    <Sparkles size={25} />
                  </div>

                  <h3>Processing your content</h3>

                  <p>{databaseStatus}</p>

                  <div className="processing-steps">
                    <span className="completed">
                      <Check size={13} />
                      Input received
                    </span>

                    <span className="completed">
                      <Check size={13} />
                      Block analysis
                    </span>

                    <span className="current">
                      <span className="tiny-spinner" />
                      Translation + verification
                    </span>
                  </div>
                </div>
              ) : showResult ? (
                <div className="result-content">
                  <div className="result-toolbar">
                    <span>
                      {selectedFiles.length
                        ? "Translated document result"
                        : "Translated text result"}
                    </span>

                    <div>
                      <button
                        className="mini-button"
                        onClick={copyTranslation}
                      >
                        <Copy size={14} />
                        Copy
                      </button>

                      <button
                        className="mini-button"
                        onClick={downloadTranslation}
                      >
                        <Download size={14} />
                        Export
                      </button>
                    </div>
                  </div>

                  <div className="translation-output">
                    {translationResult}
                  </div>

                  <div className="quality-grid">
                    <div className="quality-card">
                      <div className="quality-icon">
                        <Check size={16} />
                      </div>
                      <div>
                        <span>Accuracy</span>
                        <strong>{accuracy}%</strong>
                      </div>
                      <div className="quality-bar">
                        <span style={{ width: `${accuracy}%` }} />
                      </div>
                    </div>

                    <div className="quality-card">
                      <div className="quality-icon confidence">
                        <Sparkles size={16} />
                      </div>
                      <div>
                        <span>Confidence</span>
                        <strong>{confidence}%</strong>
                      </div>
                      <div className="quality-bar">
                        <span style={{ width: `${confidence}%` }} />
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-result">
                  <div className="empty-result-icon">
                    <Languages size={24} />
                  </div>

                  <h3>Your translation will appear here</h3>

                  <p>
                    Upload or enter Chinese content, then select{" "}
                    <strong>Translate</strong>.
                  </p>

                  <div className="empty-flow">
                    <span>OCR</span>
                    <ChevronRight size={14} />
                    <span>Block analysis</span>
                    <ChevronRight size={14} />
                    <span>Retrieval</span>
                    <ChevronRight size={14} />
                    <span>Translation</span>
                  </div>
                </div>
              )}
            </section>
          </div>

          <section className="pipeline-card">
            <div className="pipeline-header">
              <div>
                <span className="panel-kicker">03 · INTELLIGENCE FLOW</span>
                <h2>How TransFusion AI processes your content</h2>
              </div>

              <div className="pipeline-status">
                <Database size={15} />
                {databaseStatus}
              </div>
            </div>

            <div className="pipeline">
              <div className="pipeline-step">
                <span>01</span>
                <div>
                  <strong>Detect</strong>
                  <small>OCR / text input</small>
                </div>
              </div>

              <div className="pipeline-line" />

              <div className="pipeline-step">
                <span>02</span>
                <div>
                  <strong>Block</strong>
                  <small>Contextual segmentation</small>
                </div>
              </div>

              <div className="pipeline-line" />

              <div className="pipeline-step">
                <span>03</span>
                <div>
                  <strong>Retrieve</strong>
                  <small>Database first</small>
                </div>
              </div>

              <div className="pipeline-line" />

              <div className="pipeline-step">
                <span>04</span>
                <div>
                  <strong>Translate</strong>
                  <small>Context-aware agent</small>
                </div>
              </div>

              <div className="pipeline-line" />

              <div className="pipeline-step">
                <span>05</span>
                <div>
                  <strong>Verify</strong>
                  <small>Accuracy + confidence</small>
                </div>
              </div>
            </div>
          </section>

          {showResult && (
            <section className="privacy-card">
              <div className="privacy-icon">
                <ShieldCheck size={21} />
              </div>

              <div className="privacy-content">
                <span className="panel-kicker">04 · PRIVACY CONTROL</span>

                <h2>Would you like to add this translation to our database?</h2>

                <p>
                  Your translation is already available in your history. If
                  you approve it, eligible translation content can also become
                  reusable knowledge for future translations.
                </p>

                <div className="privacy-actions">
                  <button
                    className={`save-button ${saveDecision === "saved" ? "selected" : ""
                      }`}
                    onClick={saveToDatabase}
                  >
                    <Database size={16} />
                    Yes, save to database
                  </button>

                  <button
                    className={`private-button ${saveDecision === "private" ? "selected" : ""
                      }`}
                    onClick={keepPrivate}
                  >
                    <ShieldCheck size={16} />
                    No, keep private
                  </button>
                </div>

                {saveDecision && (
                  <div className="decision-message">
                    <Check size={14} />

                    {saveDecision === "saved"
                      ? "Saved to history and approved for reusable database storage."
                      : "Kept private. This translation remains available in your history only."}
                  </div>
                )}
              </div>
            </section>
          )}

          <div className="workspace-footer">
            <div>
              <Bot size={15} />
              TransFusion AI
            </div>

            <span>
              Context-aware multilingual OCR & translation workspace
            </span>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;