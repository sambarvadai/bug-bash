import { useRef, useState, useEffect, useCallback } from "react";
import Editor, { useMonaco } from "@monaco-editor/react";

export default function CodeEditor({
  challenge,
  running,
  hintShown,
  onRun,
  onHint,
}) {
  const monaco = useMonaco();
  const editorRef = useRef(null);
  const modelsRef = useRef({});
  const [activeFile, setActiveFile] = useState(challenge.files[0].name);

  // Create one Monaco model per file when monaco becomes available
  useEffect(() => {
    if (!monaco) return;

    // Dispose any leftover models from a previous mount (shouldn't happen with key=, but safe)
    Object.values(modelsRef.current).forEach((m) => m.dispose());
    modelsRef.current = {};

    for (const file of challenge.files) {
      const uri = monaco.Uri.parse(`file:///${challenge.id}/${file.name}`);
      // If model already exists (hot-reload edge case), reuse it
      const existing = monaco.editor.getModel(uri);
      if (existing) {
        existing.setValue(file.initial_code);
        modelsRef.current[file.name] = existing;
      } else {
        modelsRef.current[file.name] = monaco.editor.createModel(
          file.initial_code,
          "python",
          uri
        );
      }
    }

    // If editor is already mounted, switch to first file's model
    if (editorRef.current) {
      editorRef.current.setModel(modelsRef.current[challenge.files[0].name]);
    }

    setActiveFile(challenge.files[0].name);

    return () => {
      Object.values(modelsRef.current).forEach((m) => m.dispose());
      modelsRef.current = {};
    };
  }, [monaco, challenge]);

  const handleEditorMount = useCallback(
    (editor) => {
      editorRef.current = editor;
      // Set model if models already created (monaco was ready before mount)
      if (modelsRef.current[activeFile]) {
        editor.setModel(modelsRef.current[activeFile]);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const switchTab = (filename) => {
    setActiveFile(filename);
    if (editorRef.current && modelsRef.current[filename]) {
      editorRef.current.setModel(modelsRef.current[filename]);
      editorRef.current.focus();
    }
  };

  const handleRun = () => {
    const files = {};
    for (const [name, model] of Object.entries(modelsRef.current)) {
      files[name] = model.getValue();
    }
    onRun(files);
  };

  const handleReset = () => {
    for (const file of challenge.files) {
      const model = modelsRef.current[file.name];
      if (model) model.setValue(file.initial_code);
    }
  };

  return (
    <div className="editor-section">
      <div className="tab-bar">
        {challenge.files.map((file) => (
          <button
            key={file.name}
            className={`tab${activeFile === file.name ? " active" : ""}`}
            onClick={() => switchTab(file.name)}
          >
            {file.name}
          </button>
        ))}
      </div>

      <div className="monaco-wrapper">
        <Editor
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          onMount={handleEditorMount}
          options={{
            fontSize: 13,
            fontFamily: "'Cascadia Code', 'Fira Code', 'Courier New', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            lineNumbers: "on",
            renderLineHighlight: "all",
            tabSize: 4,
            insertSpaces: true,
            wordWrap: "off",
            automaticLayout: true,
          }}
        />
      </div>

      <div className="editor-actions">
        <button
          className="btn btn-primary"
          onClick={handleRun}
          disabled={running}
        >
          {running ? "Running…" : "▶ Run Tests"}
        </button>
        {!hintShown && (
          <button className="btn btn-secondary" onClick={onHint}>
            💡 Hint
          </button>
        )}
        <button className="btn btn-secondary" onClick={handleReset}>
          ↺ Reset
        </button>
        {hintShown && (
          <div className="hint-box">
            <strong>Hint:</strong> {challenge.hint}
          </div>
        )}
      </div>
    </div>
  );
}
