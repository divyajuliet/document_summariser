import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  // Remember the selected theme
  useEffect(() => {
    const savedTheme = localStorage.getItem("unthinkable-theme");

    if (savedTheme === "dark") {
      setDarkMode(true);
    }
  }, []);

  useEffect(() => {
    document.body.className = darkMode ? "dark-theme" : "light-theme";
    localStorage.setItem(
      "unthinkable-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const analyzeDocument = async () => {
    if (!file) {
      setError("Please select a PDF or image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // ----------------------------------------------------
      // STEP 1: Upload document
      // ----------------------------------------------------

      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!uploadResponse.ok) {
        let message = "Upload failed.";

        try {
          const data = await uploadResponse.json();
          message = data.detail || message;
        } catch {
          // Keep default message
        }

        throw new Error(message);
      }

      const uploaded = await uploadResponse.json();

      // ----------------------------------------------------
      // STEP 2: Run complete document intelligence pipeline
      // ----------------------------------------------------

      const processResponse = await fetch(
        `${API_URL}/documents/${uploaded.document_id}/process`
      );

      if (!processResponse.ok) {
        let detail = "Document processing failed.";

        try {
          const data = await processResponse.json();
          detail = data.detail || detail;
        } catch {
          // Keep default message
        }

        // No readable text in an image/document
        if (processResponse.status === 422) {
          throw new Error(
            "No readable document text was detected. Please upload a PDF, scanned document, or image containing text."
          );
        }

        throw new Error(detail);
      }

      const processed = await processResponse.json();

      // ----------------------------------------------------
      // STEP 3: Store complete result
      // ----------------------------------------------------

      setResult({
        ...uploaded,
        ...processed,
      });
    } catch (err) {
      console.error("Document processing error:", err);

      setError(
        err.message ||
          "Something went wrong while processing the document."
      );
    } finally {
      setLoading(false);
    }
  };

  const formatPercentage = (value) => {
    if (value === undefined || value === null) {
      return "—";
    }

    return `${Math.round(value * 100)}%`;
  };

  const getRiskClass = (risk) => {
    if (!risk) return "";

    return risk.toLowerCase().replace(/\s+/g, "-");
  };

  const getStatusClass = (status) => {
    if (!status) return "";

    return status.toLowerCase().replace(/\s+/g, "-");
  };

  return (
    <div className="app">
      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="header">
        <div className="brand">
          <div className="brand-icon">U</div>

          <div>
            <h1>Unthinkable</h1>
            <p>Self-Verifying Document Intelligence</p>
          </div>
        </div>

        <button
          className="theme-toggle"
          onClick={() => setDarkMode((current) => !current)}
          type="button"
        >
          {darkMode ? "☀ Light" : "☾ Dark"}
        </button>
      </header>

      {/* ================================================== */}
      {/* MAIN */}
      {/* ================================================== */}

      <main className="container">

        {/* HERO */}
        <section className="hero">
          <h2>Verify what they say.</h2>

          <p>
            Upload a document and let Unthinkable extract,
            summarize, question, verify, and challenge its contents.
          </p>
        </section>

        {/* ================================================== */}
        {/* UPLOAD CARD */}
        {/* ================================================== */}

        <section className="upload-card">

          <label className="upload-area">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              hidden
            />

            <div className="upload-icon">
              ↑
            </div>

            <strong>
              {file ? file.name : "Choose a document"}
            </strong>

            <span>
              PDF, PNG, JPG or JPEG
            </span>
          </label>

          <button
            className="analyze-button"
            onClick={analyzeDocument}
            disabled={loading}
            type="button"
          >
            {loading
              ? "Analyzing document..."
              : "Analyze Document →"}
          </button>
        </section>

        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (
          <section className="error-card">
            <strong>Processing failed</strong>

            <p>{error}</p>
          </section>
        )}

        {/* ================================================== */}
        {/* RESULTS */}
        {/* ================================================== */}

        {result && (
          <section className="results">

            {/* ---------------------------------------------- */}
            {/* DOCUMENT OVERVIEW */}
            {/* ---------------------------------------------- */}

            <div className="section-heading">
              <h2>Analysis Results</h2>
            </div>

            <div className="stats-grid">

              <div className="stat-card">
                <span>Document</span>
                <strong>
                  {result.original_filename ||
                    result.document?.document_id ||
                    "Document"}
                </strong>
              </div>

              <div className="stat-card">
                <span>Pages</span>
                <strong>
                  {result.document?.total_pages ?? "—"}
                </strong>
              </div>

              <div className="stat-card">
                <span>Characters</span>
                <strong>
                  {result.document?.total_characters ?? "—"}
                </strong>
              </div>

              <div className="stat-card">
                <span>Status</span>
                <strong>Processed</strong>
              </div>

            </div>

            {/* ---------------------------------------------- */}
            {/* SUMMARY */}
            {/* ---------------------------------------------- */}

            {result.summary?.summary && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Summary</h3>
                </div>

                <p className="summary-text">
                  {result.summary.summary}
                </p>

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* VERIFICATION */}
            {/* ---------------------------------------------- */}

            {result.verification && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Verification</h3>
                </div>

                <div className="verification-score">
                  {formatPercentage(
                    result.verification.overall_score
                  )}
                </div>

                <div className="metrics-grid">

                  <div className="metric">
                    <span>Factuality</span>
                    <strong>
                      {formatPercentage(
                        result.verification.factuality
                      )}
                    </strong>
                  </div>

                  <div className="metric">
                    <span>Evidence Coverage</span>
                    <strong>
                      {formatPercentage(
                        result.verification.evidence_coverage
                      )}
                    </strong>
                  </div>

                  <div className="metric">
                    <span>Consistency</span>
                    <strong>
                      {formatPercentage(
                        result.verification.consistency
                      )}
                    </strong>
                  </div>

                  <div className="metric">
                    <span>Completeness</span>
                    <strong>
                      {formatPercentage(
                        result.verification.completeness
                      )}
                    </strong>
                  </div>

                  <div className="metric">
                    <span>Numerical Consistency</span>
                    <strong>
                      {formatPercentage(
                        result.verification.numerical_consistency
                      )}
                    </strong>
                  </div>

                  <div className="metric">
                    <span>Contradiction Penalty</span>
                    <strong>
                      {formatPercentage(
                        result.verification.contradiction_penalty
                      )}
                    </strong>
                  </div>

                </div>

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* CLAIMS */}
            {/* ---------------------------------------------- */}

            {result.claims?.length > 0 && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Claims</h3>

                  <span className="count-badge">
                    {result.claims.length}
                  </span>
                </div>

                <div className="claims-list">

                  {result.claims.map((claim, index) => (
                    <details
                      className="claim-item"
                      key={
                        claim.claim_id ||
                        `claim-${index}`
                      }
                    >

                      <summary>

                        <div className="claim-summary">

                          <span className="claim-type">
                            {claim.claim_type}
                          </span>

                          <strong>
                            {formatPercentage(
                              claim.confidence
                            )} confidence
                          </strong>

                          <span
                            className={`risk-badge ${getRiskClass(
                              claim.risk
                            )}`}
                          >
                            {claim.risk}
                          </span>

                        </div>

                      </summary>

                      <div className="claim-content">

                        <p>
                          {claim.claim_text}
                        </p>

                        {claim.evidence && (
                          <div className="evidence-box">

                            <strong>
                              Evidence
                            </strong>

                            {claim.evidence.page_number && (
                              <span>
                                Page{" "}
                                {claim.evidence.page_number}
                              </span>
                            )}

                            {claim.evidence.text && (
                              <p>
                                {claim.evidence.text}
                              </p>
                            )}

                          </div>
                        )}

                      </div>

                    </details>
                  ))}

                </div>

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* VERIFICATION QUESTIONS */}
            {/* ---------------------------------------------- */}

            {result.questions?.length > 0 && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Verification Questions</h3>

                  <span className="count-badge">
                    {result.questions.length}
                  </span>
                </div>

                <div className="questions-list">

                  {result.questions.map(
                    (question, index) => (
                      <div
                        className="question-item"
                        key={
                          question.question_id ||
                          `question-${index}`
                        }
                      >

                        <span className="question-type">
                          {question.question_type}
                        </span>

                        <p>
                          {question.question}
                        </p>

                        <span className="priority">
                          Priority:{" "}
                          <strong>
                            {question.priority}
                          </strong>
                        </span>

                      </div>
                    )
                  )}

                </div>

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* VERIFICATION RESULTS */}
            {/* ---------------------------------------------- */}

            {result.verification_results?.length > 0 && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Claim Verification Results</h3>

                  <span className="count-badge">
                    {result.verification_results.length}
                  </span>
                </div>

                <div className="verification-results">

                  {result.verification_results.map(
                    (item, index) => (
                      <details
                        className="verification-item"
                        key={
                          item.claim_id ||
                          `verification-${index}`
                        }
                      >

                        <summary>

                          <div>
                            <strong>
                              {item.verification_status}
                            </strong>

                            <span
                              className={`status-badge ${getStatusClass(
                                item.verification_status
                              )}`}
                            >
                              {formatPercentage(
                                item.verification_score
                              )}
                            </span>
                          </div>

                        </summary>

                        <div className="verification-content">

                          <p>
                            {item.claim_text}
                          </p>

                          <p>
                            {item.explanation}
                          </p>

                          {item.evidence_pages?.length >
                            0 && (
                            <span>
                              Evidence pages:{" "}
                              {item.evidence_pages.join(
                                ", "
                              )}
                            </span>
                          )}

                        </div>

                      </details>
                    )
                  )}

                </div>

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* DEVIL'S ADVOCATE */}
            {/* ---------------------------------------------- */}

            {result.devils_advocate && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Devil's Advocate</h3>
                </div>

                <div className="verification-score">
                  {formatPercentage(
                    result.devils_advocate.overall_score
                  )}
                </div>

                {result.devils_advocate.results?.length >
                  0 && (
                  <div className="devils-results">

                    {result.devils_advocate.results.map(
                      (item, index) => (
                        <details
                          className="devil-item"
                          key={index}
                        >

                          <summary>

                            <div>
                              <strong>
                                {item.status ||
                                  item.challenge_type ||
                                  "Finding"}
                              </strong>

                              <span>
                                {formatPercentage(
                                  item.score
                                )}
                              </span>
                            </div>

                          </summary>

                          <div className="devil-content">

                            {item.challenge && (
                              <p>
                                <strong>
                                  Challenge:
                                </strong>{" "}
                                {item.challenge}
                              </p>
                            )}

                            {item.explanation && (
                              <p>
                                {item.explanation}
                              </p>
                            )}

                            {item.evidence_pages?.length >
                              0 && (
                              <p>
                                Evidence pages:{" "}
                                {item.evidence_pages.join(
                                  ", "
                                )}
                              </p>
                            )}

                          </div>

                        </details>
                      )
                    )}

                  </div>
                )}

              </section>
            )}

            {/* ---------------------------------------------- */}
            {/* REVISION */}
            {/* ---------------------------------------------- */}

            {result.revision && (
              <section className="result-card">

                <div className="card-header">
                  <h3>Revision</h3>
                </div>

                <div className="revision-grid">

                  <div>
                    <span>Version</span>
                    <strong>
                      {result.revision.version ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Status</span>
                    <strong>
                      {result.revision.status ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Verification Score</span>
                    <strong>
                      {formatPercentage(
                        result.revision.verification_score
                      )}
                    </strong>
                  </div>

                </div>

                {result.revision.reason && (
                  <p className="revision-reason">
                    {result.revision.reason}
                  </p>
                )}

              </section>
            )}

          </section>
        )}
      </main>

      {/* ================================================== */}
      {/* FOOTER */}
      {/* ================================================== */}

      <footer className="footer">
        <strong>Unthinkable</strong>
        <span>Self-Verifying Document Intelligence</span>
      </footer>
    </div>
  );
}

export default App;