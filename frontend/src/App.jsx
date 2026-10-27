import { useState } from "react";
import "./App.css";

function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // =========================
  // FILE HANDLER
  // =========================

  const handleFile = (file) => {
    if (!file) return;

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!allowedTypes.includes(file.type)) {
      alert("Please upload a PDF or DOCX file.");
      return;
    }

    setResume(file);
  };

  // =========================
  // ANALYZE RESUME
  // =========================

  const handleAnalyze = async () => {

    // Check Job Description
    if (!jobDescription.trim()) {
      alert("Please enter the job description.");
      return;
    }

    // Check Resume
    if (!resume) {
      alert("Please upload a resume.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      // Create FormData
      const formData = new FormData();

      // Add Job Description
      formData.append(
        "job_description",
        jobDescription
      );

      // Add Resume
      formData.append(
        "resume",
        resume
      );

      // Send request to backend
     const response = await fetch(
  "https://ai-resume-score-08ih.onrender.com/api/analyze",
  {
    method: "POST",
    body: formData,
  }
);

      // Get JSON response
      const data = await response.json();

      console.log("Backend Response:", data);

      console.log("FULL RESULT:", JSON.stringify(result, null, 2));

      // Backend error
      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Resume analysis failed."
        );
      }

      // Save result
      setResult(data);

    } catch (error) {

      console.error(error);

      setError(
        error.message ||
        "Unable to connect to backend."
      );

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="app">

      {/* =========================
          NAVBAR
      ========================= */}

      <nav className="navbar">

        <div className="logo">
          <span className="logo-icon">AI</span>
          Resume<span>Score</span>
        </div>

        <div className="nav-status">
          <span className="status-dot"></span>
          AI Screening
        </div>

      </nav>


      {/* =========================
          MAIN
      ========================= */}

      <main className="main-container">

        {/* HERO */}

        <section className="hero">

          <div className="badge">
            ✦ AI-POWERED RESUME SCREENING
          </div>

          <h1>
            Find the right candidate
            <br />
            <span>with AI-powered analysis.</span>
          </h1>

          <p className="hero-description">
            Upload a resume, provide the job description,
            and get an intelligent compatibility score
            with detailed insights.
          </p>

        </section>


        {/* =========================
            INPUTS
        ========================= */}

        <section className="workspace">


          {/* JOB DESCRIPTION */}

          <div className="card">

            <div className="card-header">

              <div>

                <span className="step-number">
                  01
                </span>

                <h2>
                  Job Description
                </h2>

              </div>

              <span className="required">
                Required
              </span>

            </div>


            <p className="card-description">
              Paste the job description you want
              to evaluate the candidate against.
            </p>


            <textarea
              value={jobDescription}
              onChange={(e) =>
                setJobDescription(e.target.value)
              }
              placeholder="Paste your job description here..."
            />


            <div className="character-count">
              {jobDescription.length} characters
            </div>

          </div>


          {/* =========================
              RESUME UPLOAD
          ========================= */}

          <div className="card">

            <div className="card-header">

              <div>

                <span className="step-number">
                  02
                </span>

                <h2>
                  Upload Resume
                </h2>

              </div>

              <span className="required">
                Required
              </span>

            </div>


            <p className="card-description">
              Upload the candidate's resume
              in PDF or DOCX format.
            </p>


            <div className="upload-box">

              {resume ? (

                <div className="selected-file">

                  <div className="file-icon">
                    📄
                  </div>

                  <div className="file-info">

                    <strong>
                      {resume.name}
                    </strong>

                    <span>
                      {(resume.size / 1024 / 1024).toFixed(2)}
                      {" "}MB
                    </span>

                  </div>

                  <button
                    className="remove-file"
                    onClick={() => setResume(null)}
                  >
                    ×
                  </button>

                </div>

              ) : (

                <>

                  <div className="upload-icon">
                    ↑
                  </div>

                  <h3>
                    Drop your resume here
                  </h3>

                  <p>
                    or{" "}
                    <label htmlFor="resume-upload">
                      browse files
                    </label>
                  </p>

                  <span className="file-types">
                    PDF or DOCX • Max 10 MB
                  </span>

                  <input
                    id="resume-upload"
                    type="file"
                    accept=".pdf,.docx"
                    hidden
                    onChange={(e) =>
                      handleFile(
                        e.target.files[0]
                      )
                    }
                  />

                </>

              )}

            </div>

          </div>

        </section>


        {/* =========================
            ANALYZE BUTTON
        ========================= */}

        <div className="analyze-section">

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={loading}
          >

            <span>
              {loading
                ? "Analyzing Resume..."
                : "Analyze Resume"}
            </span>

            <span className="arrow">
              {loading ? "..." : "→"}
            </span>

          </button>


          <p>
            Your resume is processed temporarily
            and is not stored.
          </p>

        </div>


        {/* =========================
            ERROR
        ========================= */}

        {error && (

          <div className="error-box">

            <strong>
              Analysis Failed
            </strong>

            <p>
              {error}
            </p>

          </div>

        )}


        {/* =========================
            RESULT
        ========================= */}

        {result && result.candidates?.length > 0 && (
          <div className="result-box">

            {/* =========================
        RESULT HEADER
    ========================= */}

            <div className="result-header">

              <p className="result-label">
                ANALYSIS COMPLETE
              </p>

              <h2>
                {result.candidates[0].name}
              </h2>

              <div className="score-circle">
                <span>
                  {result.candidates[0].score}%
                </span>
              </div>

              <p className="score-text">
                Resume Match Score
              </p>

            </div>


            {/* =========================
        AI CONCLUSION
    ========================= */}

            <div className="result-section">

              <h3>AI Conclusion</h3>

              <p className="conclusion">
                {result.candidates[0].details?.final_verdict ||
                  "No conclusion available."}
              </p>

            </div>


            {/* =========================
        SKILLS
    ========================= */}

            <div className="result-section">

              <div className="skills-grid">

                {/* MATCHING SKILLS */}

                <div className="skill-card">

                  <h3>
                    Matching Skills
                  </h3>

                  <div className="skills-container">

                    {result.candidates[0].details?.matching_skills?.length > 0 ? (

                      result.candidates[0].details.matching_skills.map(
                        (skill, index) => (
                          <span
                            className="skill-tag matching"
                            key={index}
                          >
                            {skill}
                          </span>
                        )
                      )

                    ) : (

                      <p>No matching skills found.</p>

                    )}

                  </div>

                </div>


                {/* MISSING SKILLS */}

                <div className="skill-card">

                  <h3>
                    Missing Important Skills
                  </h3>

                  <div className="skills-container">

                    {result.candidates[0].details
                      ?.missing_important_skills?.length > 0 ? (

                      result.candidates[0].details.missing_important_skills.map(
                        (skill, index) => (
                          <span
                            className="skill-tag missing"
                            key={index}
                          >
                            {skill}
                          </span>
                        )
                      )

                    ) : (

                      <p className="no-missing">
                        No important skills missing.
                      </p>

                    )}

                  </div>

                </div>

              </div>

            </div>


            {/* =========================
        EXPERIENCE + EDUCATION
    ========================= */}

            <div className="result-section">

              <div className="info-grid">

                {/* EXPERIENCE */}

                <div className="info-card">

                  <h3>
                    Experience
                  </h3>

                  <p>
                    {result.candidates[0].experience_years ?? 0} years
                  </p>

                </div>


                {/* EDUCATION */}

                <div className="info-card">

                  <h3>
                    Education
                  </h3>

                  {result.candidates[0].education?.length > 0 ? (

                    result.candidates[0].education.map(
                      (edu, index) => (
                        <p key={index}>
                          {edu}
                        </p>
                      )
                    )

                  ) : (

                    <p>
                      No education information available.
                    </p>

                  )}

                </div>

              </div>

            </div>


            {/* =========================
        PROJECTS
    ========================= */}

            <div className="result-section">

              <h3>
                Projects
              </h3>

              {result.candidates[0].projects?.length > 0 ? (

                result.candidates[0].projects.map(
                  (project, index) => (
                    <div
                      className="project-card"
                      key={index}
                    >
                      {project}
                    </div>
                  )
                )

              ) : (

                <p>
                  No projects found.
                </p>

              )}

            </div>


            {/* =========================
        CERTIFICATIONS
    ========================= */}

            <div className="result-section">

              <h3>
                Certifications
              </h3>

              {result.candidates[0].certifications?.length > 0 ? (

                <div>

                  {result.candidates[0].certifications.map(
                    (cert, index) => (
                      <span
                        className="certification"
                        key={index}
                      >
                        {cert}
                      </span>
                    )
                  )}

                </div>

              ) : (

                <p>
                  No certifications found.
                </p>

              )}

            </div>

          </div>



        )}

      </main>

    </div>
  );
}

export default App;