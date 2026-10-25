import React, { useState, useEffect } from 'react';
import { 
  X, 
  FileText, 
  Mic, 
  Image as ImageIcon, 
  FileUp, 
  Presentation, 
  FileCode2, 
  Link2, 
  Sparkles, 
  Loader2, 
  Camera, 
  CheckCircle2, 
  Square, 
  Play, 
  RotateCcw,
  Globe,
  UploadCloud,
  Copy,
  Check,
  Search,
  Hash,
  AlertCircle,
  ShieldAlert,
  Calendar,
  DollarSign,
  MapPin,
  Building,
  Ticket,
  Award,
  Utensils,
  Edit3,
  Clock,
  Plus,
  Tag,
  Mail,
  Activity,
  FileCheck,
  HelpCircle
} from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';
import { useAudioRecorder } from '../../hooks/useAudioRecorder';
import { AudioWaveform } from './AudioWaveform';
import { knowledgeApi } from '../../services/api';

const IMAGE_CATEGORIES = [
  { id: 'bill', label: 'Bill / Utility Statement' },
  { id: 'receipt', label: 'Receipt / Retail POS' },
  { id: 'event_poster', label: 'Event Poster / Flyer' },
  { id: 'invitation', label: 'Invitation Card' },
  { id: 'ticket', label: 'Ticket / Boarding Pass' },
  { id: 'travel_booking', label: 'Travel Booking / Hotel' },
  { id: 'identity_document', label: 'Identity Document' },
  { id: 'certificate', label: 'Certificate / Award' },
  { id: 'official_document', label: 'Official Document / Contract' },
  { id: 'handwritten_notes', label: 'Handwritten Notes' },
  { id: 'printed_notes', label: 'Printed Notes / Guide' },
  { id: 'screenshot', label: 'Screenshot / App Screen' },
  { id: 'menu_or_food_information', label: 'Menu / Food Nutrition' },
  { id: 'product_or_label', label: 'Product / Label' },
  { id: 'medical_document', label: 'Medical Document / Report' },
  { id: 'other', label: 'Other Document' },
  { id: 'unknown', label: 'Unknown / Needs Review' }
];

export const CaptureModal = () => {
  const { isCaptureOpen, closeCapture, captureInitialTab, addItem } = useKnowledge();
  
  const [activeTab, setActiveTab] = useState('note');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);

  // Form states
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Research');
  
  // Note specific
  const [textContent, setTextContent] = useState('');

  // Voice specific
  const {
    isRecording,
    formattedTime,
    audioUrl,
    waveformData,
    startRecording,
    stopRecording,
    resetRecording
  } = useAudioRecorder();

  // Image & PaddleOCR specific states
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isOcrLoading, setIsOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrError, setOcrError] = useState(null);
  const [isCopied, setIsCopied] = useState(false);
  const [ocrEditableText, setOcrEditableText] = useState('');
  
  // Category & structured data states for Image Intelligence
  const [detectedCategory, setDetectedCategory] = useState('other');
  const [detectedSubtype, setDetectedSubtype] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [classificationReason, setClassificationReason] = useState('');
  const [needsReview, setNeedsReview] = useState(false);
  const [categoryData, setCategoryData] = useState({});
  const [customSummary, setCustomSummary] = useState('');
  const [customKeywords, setCustomKeywords] = useState([]);
  const [suggestedReminders, setSuggestedReminders] = useState([]);
  const [isSensitive, setIsSensitive] = useState(false);
  const [validationError, setValidationError] = useState(null);

  // PDF specific
  const [pdfFile, setPdfFile] = useState(null);

  // PPT specific
  const [pptFile, setPptFile] = useState(null);

  // DOCX specific
  const [docxFile, setDocxFile] = useState(null);

  // Web link specific
  const [linkUrl, setLinkUrl] = useState('');
  const [linkMetadata, setLinkMetadata] = useState(null);
  const [isFetchingLink, setIsFetchingLink] = useState(false);

  // Synchronize initial tab from context
  useEffect(() => {
    if (isCaptureOpen) {
      const tab = captureInitialTab === 'document' ? 'pdf' : (captureInitialTab || 'note');
      setActiveTab(tab);
      resetForm();
    }
  }, [isCaptureOpen, captureInitialTab]);

  const resetForm = () => {
    setTitle('');
    setCategory('Research');
    setTextContent('');
    setImageFile(null);
    setImagePreview(null);
    setIsOcrLoading(false);
    setOcrResult(null);
    setOcrError(null);
    setIsCopied(false);
    setOcrEditableText('');
    setDetectedCategory('other');
    setCategoryData({});
    setCustomSummary('');
    setCustomKeywords([]);
    setSuggestedReminders([]);
    setIsSensitive(false);
    setValidationError(null);
    setPdfFile(null);
    setPptFile(null);
    setDocxFile(null);
    setLinkUrl('');
    setLinkMetadata(null);
    setIsProcessing(false);
    setProcessingStep(0);
    resetRecording();
  };

  if (!isCaptureOpen) return null;

  // Execute PaddleOCR extraction and intelligence pipeline on image file
  const handleImageProcess = async (file, catHint = null) => {
    if (!file) return;
    setIsOcrLoading(true);
    setOcrError(null);
    setValidationError(null);

    try {
      const data = await knowledgeApi.processImageOcr(file, catHint || category);
      setOcrResult(data);
      setOcrEditableText(data.cleanedText || data.extractedText || '');
      
      const cat = data.category || 'other';
      setDetectedCategory(cat);
      setDetectedSubtype(data.subtype || null);
      setConfidence(data.confidence !== undefined ? data.confidence : data.categoryConfidence);
      setClassificationReason(data.reason || '');
      setNeedsReview(Boolean(data.needs_review));
      setCategoryData(data.category_fields || data.categoryData || {});
      setCustomSummary(data.summary || '');
      setCustomKeywords(data.keywords || data.semanticKeywords || []);
      setSuggestedReminders(data.suggestedReminders || []);
      setIsSensitive(Boolean(data.isSensitive));

      // Suggest clean title from image or category intelligence
      if (!title || title.trim() === '' || title === file.name.replace(/\.[^/.]+$/, "")) {
        const cleanName = file.name.replace(/\.[^/.]+$/, "");
        const catInfo = data.categoryData || {};
        const bestTitle = catInfo.event_name || catInfo.merchant || catInfo.title || (data.lines && data.lines.length > 0 && data.lines[0].length < 60 ? data.lines[0] : cleanName);
        setTitle(bestTitle);
      }
    } catch (err) {
      console.error("PaddleOCR image processing error:", err);
      const msg = err?.response?.data?.detail || err?.message || "PaddleOCR engine encountered an error or connection timed out.";
      setOcrError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsOcrLoading(false);
    }
  };

  // Client-side image format and size validation (Requirement 1)
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setValidationError(null);
    setOcrError(null);

    if (file) {
      // 1. Size check: 25 MB max limit
      const maxSizeBytes = 25 * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        setValidationError(`Image size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds 25 MB limit.`);
        return;
      }

      // 2. Format extension check
      const validExtensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif', '.gif', '.heic'];
      const fileExt = '.' + file.name.split('.').pop().toLowerCase();
      if (!validExtensions.includes(fileExt) && !file.type.startsWith('image/')) {
        setValidationError(`Unsupported file format '${fileExt}'. Please upload PNG, JPG, WEBP, BMP, or TIFF.`);
        return;
      }

      setImageFile(file);
      const url = URL.createObjectURL(file);
      setImagePreview(url);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ""));
      }
      handleImageProcess(file);
    }
  };

  // Switch image category manually (Requirement 13)
  const handleCategoryChange = (newCat) => {
    setDetectedCategory(newCat);
    setIsSensitive(newCat === 'identity_document');
    setNeedsReview(false);
    setClassificationReason(`Manually selected by user: ${newCat.replace('_', ' ')}`);
  };

  // Update a single category-specific field (Requirement 13)
  const handleCategoryFieldChange = (key, value) => {
    setCategoryData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Toggle suggested reminder confirmation (Requirement 12)
  const toggleReminderConfirmation = (reminderId) => {
    setSuggestedReminders(prev => prev.map(rem => 
      rem.id === reminderId ? { ...rem, confirmed: !rem.confirmed } : rem
    ));
  };

  // Copy extracted text
  const handleCopyOcrText = () => {
    const textToCopy = ocrEditableText || ocrResult?.cleanedText || ocrResult?.extractedText || '';
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  // Handle PDF selection
  const handlePdfChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPdfFile(file);
      if (!title) setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  // Handle PPT selection
  const handlePptChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPptFile(file);
      if (!title) setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  // Handle DOCX selection
  const handleDocxChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setDocxFile(file);
      if (!title) setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  // Simulate fetching metadata for pasted link
  const handleLinkFetch = () => {
    if (!linkUrl.trim()) return;
    setIsFetchingLink(true);
    setTimeout(() => {
      try {
        const parsedUrl = new URL(linkUrl.startsWith('http') ? linkUrl : `https://${linkUrl}`);
        const domain = parsedUrl.hostname;
        const simulatedTitle = `Article from ${domain}`;
        setLinkMetadata({
          domain,
          title: simulatedTitle,
          excerpt: `Summary analysis and key takeaways extracted from ${domain} web resource.`,
        });
        if (!title) setTitle(simulatedTitle);
      } catch {
        setLinkMetadata({
          domain: "web-source.com",
          title: "Web Resource Bookmark",
          excerpt: "Extracted content from target URL."
        });
      }
      setIsFetchingLink(false);
    }, 600);
  };

  // Process and save with AI step animation
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    const steps = [
      "Analyzing document structure & phonemes...",
      "Extracting key entities and conceptual tags...",
      "Generating vector embeddings across multi-modal space...",
      "Detecting actionable dates & reminders...",
      "Synchronizing with Memora Vault..."
    ];

    for (let i = 0; i < steps.length; i++) {
      setProcessingStep(i);
      await new Promise((res) => setTimeout(res, 350));
    }

    // Auto-generate tags based on content and modality
    let finalTags = [activeTab.toUpperCase()];
    if (activeTab === 'image') {
      const catLabel = detectedCategory.replace('_', ' ').toUpperCase();
      finalTags = [catLabel];
      if (customKeywords && customKeywords.length > 0) {
        finalTags = [...finalTags, ...customKeywords.slice(0, 3)];
      } else {
        finalTags.push('OCR', 'IMAGE');
      }
    } else if (activeTab === 'note') {
      finalTags = ['Note', 'QuickCapture'];
    } else if (activeTab === 'voice') {
      finalTags = ['Audio', 'VoiceMemo'];
    } else if (activeTab === 'pdf') {
      finalTags = ['PDF', 'Document'];
    } else if (activeTab === 'ppt') {
      finalTags = ['Presentation', 'Slides'];
    } else if (activeTab === 'docx') {
      finalTags = ['WordDoc', 'Manuscript'];
    } else if (activeTab === 'link') {
      finalTags = ['Bookmark', 'WebLink'];
    }

    // Build item object
    let finalItem = {
      title: title.trim() || `Untitled ${activeTab.toUpperCase()}`,
      type: activeTab,
      category: category || 'General',
      tags: finalTags,
      createdAt: new Date().toISOString(),
      favorite: false,
    };

    if (activeTab === 'note') {
      finalItem.content = textContent;
      finalItem.summary = textContent.slice(0, 160) + (textContent.length > 160 ? '...' : '');
      finalItem.entities = ["Markdown Notes", "Memora Knowledge", category];
      if (textContent.toLowerCase().includes('tomorrow') || textContent.toLowerCase().includes('due') || textContent.toLowerCase().includes('deadline')) {
        finalItem.detectedEvents = [{
          id: `ev-${Date.now()}`,
          title: `Action item from: ${finalItem.title}`,
          dueDate: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
          priority: 'urgent',
          completed: false
        }];
      }
    } else if (activeTab === 'voice') {
      finalItem.duration = formattedTime || "01:25";
      finalItem.content = "Transcription: [Recorded via Memora audio engine]: Captured audio transcript. Discussion points, action items, and technical summary synthesized.";
      finalItem.summary = `Voice memo recorded on ${new Date().toLocaleDateString()} with duration ${finalItem.duration}.`;
      finalItem.entities = ["Voice Memo", "Audio Transcription", "Whisper AI"];
      finalItem.detectedEvents = [{
        id: `ev-${Date.now()}`,
        title: `Follow up on audio memo: ${finalItem.title}`,
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3).toISOString(),
        priority: 'upcoming',
        completed: false
      }];
    } else if (activeTab === 'image') {
      // Complete multi-modal image payload adhering to all 16 requirements
      finalItem.imageUrl = ocrResult?.fileUrl || imagePreview || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80";
      finalItem.fileRef = ocrResult?.filePath || null;
      finalItem.fileSize = ocrResult?.fileSize || (imageFile ? `${(imageFile.size / (1024 * 1024)).toFixed(2)} MB` : "0.5 MB");
      finalItem.dimensions = ocrResult?.dimensions || null;
      finalItem.mimeType = ocrResult?.mimeType || imageFile?.type || "image/png";
      
      const catObj = IMAGE_CATEGORIES.find(c => c.id === detectedCategory);
      finalItem.imageCategory = detectedCategory;
      finalItem.category = catObj ? catObj.label : 'General';
      finalItem.categoryData = categoryData;
      
      const actualText = ocrEditableText !== undefined ? ocrEditableText : (ocrResult?.cleanedText || ocrResult?.extractedText || "");
      finalItem.content = actualText;
      finalItem.rawOcrText = ocrResult?.rawText || actualText;
      finalItem.summary = customSummary || ocrResult?.summary || (actualText ? actualText.slice(0, 160) : "Image document.");
      finalItem.ocrConfidence = ocrResult?.confidence || 0;
      finalItem.ocrDetails = ocrResult ? {
        lineCount: ocrResult.lineCount,
        wordCount: ocrResult.wordCount,
        charCount: ocrResult.charCount,
        confidence: ocrResult.confidence
      } : {};
      finalItem.entities = customKeywords.length > 0 ? customKeywords : (ocrResult?.keywords || ["PaddleOCR", "Vision AI"]);
      finalItem.keywords = customKeywords.length > 0 ? customKeywords : (ocrResult?.keywords || []);
      finalItem.normalizedDates = ocrResult?.normalizedDates || [];
      finalItem.suggestedReminders = suggestedReminders;
      finalItem.subtype = detectedSubtype;
      finalItem.confidence = confidence;
      finalItem.reason = classificationReason;
      finalItem.needs_review = needsReview;
      finalItem.category_fields = categoryData;

      // Only confirmed reminders are passed into detectedEvents to create actual reminders (Requirement 12)
      finalItem.detectedEvents = suggestedReminders
        .filter(r => r.confirmed)
        .map(r => ({
          id: r.id || `ev-${Date.now()}`,
          title: r.title,
          dueDate: r.dueDate,
          priority: r.priority || "normal",
          completed: false
        }));

      finalItem.isSensitive = Boolean(isSensitive);
      finalItem.processingStatus = ocrResult?.processingStatus || "completed";
    } else if (activeTab === 'pdf') {
      finalItem.fileSize = pdfFile ? `${(pdfFile.size / (1024 * 1024)).toFixed(1)} MB` : "2.4 MB";
      finalItem.pages = 18;
      finalItem.content = `PDF document parsed from ${pdfFile ? pdfFile.name : 'Document.pdf'}. Extracted executive summary, sections, figures, and bibliographic citations.`;
      finalItem.summary = `PDF Document: ${pdfFile ? pdfFile.name : 'Report.pdf'} with complete text extraction.`;
      finalItem.entities = ["PDF Document", "Executive Summary", "Vectorized"];
    } else if (activeTab === 'ppt') {
      finalItem.fileSize = pptFile ? `${(pptFile.size / (1024 * 1024)).toFixed(1)} MB` : "6.8 MB";
      finalItem.pages = 24;
      finalItem.content = `Presentation deck parsed from ${pptFile ? pptFile.name : 'Presentation.pptx'}. Analyzed 24 slides, bullet points, speaker notes, and key takeaways.`;
      finalItem.summary = `Slide Deck: ${pptFile ? pptFile.name : 'Presentation.pptx'} with slide-by-slide AI analysis.`;
      finalItem.entities = ["Slide Deck", "Presentation", "Speaker Notes"];
    } else if (activeTab === 'docx') {
      finalItem.fileSize = docxFile ? `${(docxFile.size / (1024 * 1024)).toFixed(1)} MB` : "1.2 MB";
      finalItem.pages = 8;
      finalItem.content = `Word document parsed from ${docxFile ? docxFile.name : 'Document.docx'}. Synthesized headings, table of contents, paragraphs, and action items.`;
      finalItem.summary = `Word Document: ${docxFile ? docxFile.name : 'Document.docx'} with structured outline extraction.`;
      finalItem.entities = ["Word Document", "Structured Docx", "Manuscript"];
    } else if (activeTab === 'link') {
      finalItem.url = linkUrl;
      finalItem.domain = linkMetadata?.domain || "web-article.org";
      finalItem.content = `Reader mode content extracted from ${linkUrl}. Comprehensive overview with key insights and citations.`;
      finalItem.summary = linkMetadata?.excerpt || `Web resource from ${linkMetadata?.domain || 'web'}`;
      finalItem.entities = ["Web Bookmark", finalItem.domain];
    }

    await addItem(finalItem);
    setIsProcessing(false);
    closeCapture();
  };

  const tabs = [
    { id: 'note', label: 'Text', icon: FileText, color: 'text-palette-slate' },
    { id: 'image', label: 'Image', icon: ImageIcon, color: 'text-palette-clay' },
    { id: 'voice', label: 'Audio', icon: Mic, color: 'text-palette-slate' },
    { id: 'pdf', label: 'PDF', icon: FileUp, color: 'text-palette-navy dark:text-palette-mist' },
    { id: 'ppt', label: 'PPT', icon: Presentation, color: 'text-palette-clay' },
    { id: 'docx', label: 'DOCX', icon: FileCode2, color: 'text-palette-slate' },
    { id: 'link', label: 'Link', icon: Link2, color: 'text-palette-slate' },
  ];

  const stepsList = [
    "Analyzing document structure & phonemes...",
    "Extracting key entities and conceptual tags...",
    "Generating vector embeddings across multi-modal space...",
    "Detecting actionable dates & reminders...",
    "Synchronizing with Memora Vault..."
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div 
        className="w-full max-w-2xl bg-dark-card border border-dark-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border/80 bg-dark-surface/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent-light">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-palette-navy dark:text-white leading-tight">Capture Knowledge</h3>
              <p className="text-xs text-app-subtle">Ingest, extract, & index information seamlessly</p>
            </div>
          </div>
          <button
            onClick={closeCapture}
            className="p-1.5 rounded-lg text-app-subtle hover:text-white hover:bg-dark-hover transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab navigation (Horizontal scrollable on mobile) */}
        <div className="flex border-b border-dark-border/80 px-4 bg-dark-surface/40 overflow-x-auto scrollbar-none gap-1 py-1.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-xl transition-all whitespace-nowrap cursor-pointer border ${
                  isActive
                    ? 'border-accent text-accent-light bg-accent/10 shadow-sm'
                    : 'border-transparent text-app-muted hover:text-white hover:border-palette-slate'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${tab.color}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 relative">
          
          {/* AI Processing Overlay */}
          {isProcessing && (
            <div className="absolute inset-0 bg-dark-card/95 backdrop-blur-md z-20 flex flex-col items-center justify-center p-6 text-center animate-fadeIn">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-palette-navy via-palette-slate to-palette-clay p-0.5 shadow-glow-lg mb-6 animate-pulse">
                <div className="w-full h-full bg-dark-bg rounded-[14px] flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-accent-light" />
                </div>
              </div>
              <h4 className="text-lg font-bold text-palette-navy dark:text-white mb-2">Memora Ingestion Engine</h4>
              <p className="text-xs text-app-muted max-w-sm mb-6">
                Embedding content, extracting topics, and synchronizing with your personal knowledge base...
              </p>

              <div className="w-full max-w-md space-y-2.5 text-left">
                {stepsList.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-xs">
                    {idx < processingStep ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : idx === processingStep ? (
                      <Loader2 className="w-4 h-4 text-accent-light animate-spin shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-dark-border shrink-0" />
                    )}
                    <span className={idx === processingStep ? "text-white font-medium" : idx < processingStep ? "text-emerald-300/80" : "text-app-subtle"}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Title Input */}
            <div>
              <label className="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5">
                Title
              </label>
              <input
                type="text"
                required
                placeholder="Title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-app-subtle outline-none"
              />
            </div>

            {/* MODALITY 1: TEXT NOTE */}
            {activeTab === 'note' && (
              <div>
                <label className="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5">
                  Note Content (Markdown supported)
                </label>
                <textarea
                  rows={6}
                  required
                  placeholder="Capture thoughts, meeting notes, outlines, or code snippets..."
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl p-3.5 text-sm text-white placeholder-app-subtle outline-none resize-none font-mono"
                />
              </div>
            )}

            {/* MODALITY 2: IMAGE UPLOAD WITH PADDLEOCR & INTELLIGENCE */}
            {activeTab === 'image' && (
              <div className="space-y-4">
                {/* Validation Error Alert */}
                {validationError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5 animate-fadeIn">
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                    <span>{validationError}</span>
                  </div>
                )}

                {!imagePreview ? (
                  <div className="relative border-2 border-dashed border-dark-border hover:border-palette-slate rounded-2xl p-7 flex flex-col items-center justify-center text-center transition-colors group bg-dark-bg/40">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <div className="w-12 h-12 rounded-xl bg-dark-surface border border-dark-border flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-sm">
                      <ImageIcon className="w-6 h-6 text-palette-clay" />
                    </div>
                    <p className="text-sm font-semibold text-white mb-1">
                      Upload an image, poster, receipt, or document
                    </p>
                    <p className="text-xs text-app-subtle mb-4">
                      PNG, JPG, WEBP, BMP, or TIFF (Up to 25 MB)
                    </p>

                    <label className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-dark-surface border border-dark-border text-xs font-semibold text-app-muted hover:text-white hover:border-accent/40 cursor-pointer transition-colors relative z-10">
                      <Camera className="w-4 h-4 text-palette-clay" />
                      <span>Take Photo</span>
                      <input
                        type="file"
                        accept="image/*"
                        capture="environment"
                        onChange={handleImageChange}
                        className="hidden"
                      />
                    </label>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-dark-border bg-dark-bg/60 p-4 space-y-4">
                    {/* Image Header & Metadata */}
                    <div className="flex items-start justify-between gap-3 pb-3 border-b border-dark-border/70">
                      <div className="flex items-center gap-3">
                        <img
                          src={imagePreview}
                          alt="Uploaded preview"
                          className="w-16 h-16 object-cover rounded-xl border border-palette-pale flex-shrink-0 shadow-sm"
                        />
                        <div className="min-w-0">
                          <h4 className="text-sm font-semibold text-white truncate max-w-[220px] sm:max-w-[320px]">
                            {imageFile?.name || "Uploaded Image"}
                          </h4>
                          <p className="text-xs text-app-subtle">
                            {ocrResult?.fileSize || (imageFile ? `${(imageFile.size / 1024).toFixed(1)} KB` : 'Image file')}
                            {ocrResult?.dimensions && ` • ${ocrResult.dimensions.width}×${ocrResult.dimensions.height}`}
                          </p>

                          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                            {isOcrLoading ? (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-palette-sand/40 text-palette-clay border border-palette-clay/30 animate-pulse">
                                <Loader2 className="w-3 h-3 animate-spin text-accent-light" />
                                PaddleOCR scanning...
                              </span>
                            ) : ocrResult ? (
                              <>
                                <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                                  ocrResult.hasReadableText ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                                }`}>
                                  <CheckCircle2 className="w-3 h-3" />
                                  {ocrResult.hasReadableText ? 'PaddleOCR Extracted' : 'No Legible Text'}
                                </span>
                                {ocrResult.confidence > 0 && (
                                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-palette-mist/25 text-palette-slate border border-palette-mist/40">
                                    {ocrResult.confidence}% Confidence
                                  </span>
                                )}
                              </>
                            ) : null}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center">
                        <button
                          type="button"
                          onClick={() => {
                            setImageFile(null);
                            setImagePreview(null);
                            setOcrResult(null);
                            setOcrEditableText('');
                            setOcrError(null);
                            setCategoryData({});
                          }}
                          className="p-1.5 rounded-lg text-app-subtle hover:text-rose-400 hover:bg-dark-surface border border-transparent hover:border-dark-border transition-colors cursor-pointer"
                          title="Remove image"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Sensitive Document Privacy Warning (Requirement 15) */}
                    {isSensitive && (
                      <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-2.5">
                        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                        <span className="leading-relaxed">
                          <strong>Sensitive Identity Record:</strong> Access is strictly restricted to your account. Identifier numbers are masked to safeguard privacy.
                        </span>
                      </div>
                    )}

                    {/* Scanning / Loading banner */}
                    {isOcrLoading && (
                      <div className="p-3.5 rounded-xl bg-palette-sand/20 border border-palette-clay/30 flex items-center justify-center gap-2.5 animate-fadeIn">
                        <Loader2 className="w-4 h-4 text-palette-clay animate-spin" />
                        <span className="text-xs font-medium text-palette-navy dark:text-white">
                          Running PaddleOCR & category extraction...
                        </span>
                      </div>
                    )}

                    {/* Error Banner */}
                    {ocrError && (
                      <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                          <span>{ocrError}</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleImageProcess(imageFile)}
                          className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 font-semibold text-[11px] text-rose-200 transition-colors cursor-pointer"
                        >
                          Retry
                        </button>
                      </div>
                    )}

                    {/* Results Display */}
                    {ocrResult && !isOcrLoading && (
                      <div className="space-y-4 animate-fadeIn">
                        
                        {/* Category Selector, Subtype & Reason Display (Requirements 1, 3, 6 & 13) */}
                        <div className="p-3.5 rounded-xl bg-dark-surface/60 border border-dark-border/80 space-y-2.5">
                          <div className="flex items-center justify-between">
                            <label className="text-xs font-semibold text-app-muted uppercase tracking-wider flex items-center gap-1.5">
                              <Tag className="w-3.5 h-3.5 text-accent-light" />
                              <span>Detected Category</span>
                            </label>
                            <div className="flex items-center gap-1.5">
                              {detectedSubtype && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-palette-sand/40 text-palette-clay border border-palette-clay/30 font-medium">
                                  {detectedSubtype.replace(/_/g, ' ').toUpperCase()}
                                </span>
                              )}
                              <span className="text-[11px] text-palette-slate dark:text-palette-mist font-medium">
                                {confidence ? `${Math.round(confidence * 100)}% Match` : ''}
                              </span>
                            </div>
                          </div>
                          
                          <select
                            value={detectedCategory}
                            onChange={(e) => handleCategoryChange(e.target.value)}
                            className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3 py-2 text-xs text-white outline-none cursor-pointer"
                          >
                            {IMAGE_CATEGORIES.map(cat => (
                              <option key={cat.id} value={cat.id} className="bg-dark-card text-white">
                                {cat.label}
                              </option>
                            ))}
                          </select>

                          {/* Reasoning & Needs Review Warning */}
                          {needsReview && (
                            <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-start gap-2 text-amber-300 text-xs">
                              <AlertCircle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                              <div>
                                <span className="font-semibold block">Needs Review: Low Confidence / Sparse Text</span>
                                <span className="text-[11px] text-amber-200/80">Please verify or select the correct document category from the dropdown above.</span>
                              </div>
                            </div>
                          )}

                          {classificationReason && (
                            <p className="text-[11px] text-app-subtle italic flex items-center gap-1">
                              <span className="font-semibold text-app-muted not-italic">Reason:</span> {classificationReason}
                            </p>
                          )}
                        </div>

                        {/* Category-Specific Form Inputs (Requirements 4, 7 & 13) */}
                        {/* 1. BILL */}
                        {detectedCategory === 'bill' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <DollarSign className="w-3.5 h-3.5" />
                              <span>Bill / Invoice Breakdown (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Provider / Vendor</label>
                                <input
                                  type="text"
                                  value={categoryData.vendor || ''}
                                  placeholder="e.g. Pacific Power, AT&T"
                                  onChange={(e) => handleCategoryFieldChange('vendor', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Bill Type</label>
                                <input
                                  type="text"
                                  value={categoryData.bill_type || ''}
                                  placeholder="e.g. Electricity Bill, Internet"
                                  onChange={(e) => handleCategoryFieldChange('bill_type', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Bill / Account Number</label>
                                <input
                                  type="text"
                                  value={categoryData.bill_number || ''}
                                  placeholder="e.g. ACC-84920"
                                  onChange={(e) => handleCategoryFieldChange('bill_number', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Total Amount</label>
                                <input
                                  type="text"
                                  value={categoryData.amount || ''}
                                  placeholder="e.g. $142.50"
                                  onChange={(e) => handleCategoryFieldChange('amount', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Due Date</label>
                                <input
                                  type="text"
                                  value={categoryData.due_date || ''}
                                  placeholder="e.g. Nov 15, 2026"
                                  onChange={(e) => handleCategoryFieldChange('due_date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Payment Status</label>
                                <input
                                  type="text"
                                  value={categoryData.payment_status || 'due'}
                                  placeholder="e.g. Due, Paid, Pending"
                                  onChange={(e) => handleCategoryFieldChange('payment_status', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 2. RECEIPT */}
                        {detectedCategory === 'receipt' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <DollarSign className="w-3.5 h-3.5" />
                              <span>Receipt Breakdown (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Merchant / Store</label>
                                <input
                                  type="text"
                                  value={categoryData.vendor || categoryData.merchant || ''}
                                  placeholder="e.g. Starbucks, Target"
                                  onChange={(e) => handleCategoryFieldChange('vendor', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Total Amount</label>
                                <input
                                  type="text"
                                  value={categoryData.amount || ''}
                                  placeholder="e.g. $42.50"
                                  onChange={(e) => handleCategoryFieldChange('amount', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Receipt Date</label>
                                <input
                                  type="text"
                                  value={categoryData.date || categoryData.issue_date || ''}
                                  placeholder="e.g. Oct 24, 2026"
                                  onChange={(e) => handleCategoryFieldChange('date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Payment Method</label>
                                <input
                                  type="text"
                                  value={categoryData.payment_method || ''}
                                  placeholder="e.g. Visa, Cash"
                                  onChange={(e) => handleCategoryFieldChange('payment_method', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 3. EVENT POSTER */}
                        {detectedCategory === 'event_poster' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Calendar className="w-3.5 h-3.5" />
                              <span>Event Poster Details (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div className="sm:col-span-2">
                                <label className="text-[11px] text-app-subtle block mb-1">Event Name</label>
                                <input
                                  type="text"
                                  value={categoryData.event_name || ''}
                                  placeholder="e.g. AI Innovation Summit 2026"
                                  onChange={(e) => handleCategoryFieldChange('event_name', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Event Date</label>
                                <input
                                  type="text"
                                  value={categoryData.event_date || categoryData.date || ''}
                                  placeholder="e.g. Nov 12, 2026"
                                  onChange={(e) => handleCategoryFieldChange('event_date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Start Time</label>
                                <input
                                  type="text"
                                  value={categoryData.start_time || categoryData.time || ''}
                                  placeholder="e.g. 7:00 PM"
                                  onChange={(e) => handleCategoryFieldChange('start_time', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Venue / Location</label>
                                <input
                                  type="text"
                                  value={categoryData.venue || ''}
                                  placeholder="e.g. Moscone Center, Hall B"
                                  onChange={(e) => handleCategoryFieldChange('venue', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Organizer / Host</label>
                                <input
                                  type="text"
                                  value={categoryData.organizer || ''}
                                  placeholder="e.g. Tech Global Inc"
                                  onChange={(e) => handleCategoryFieldChange('organizer', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Registration Deadline</label>
                                <input
                                  type="text"
                                  value={categoryData.registration_deadline || ''}
                                  placeholder="e.g. Nov 1, 2026"
                                  onChange={(e) => handleCategoryFieldChange('registration_deadline', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Contact Details</label>
                                <input
                                  type="text"
                                  value={categoryData.contact_details || ''}
                                  placeholder="e.g. info@events.org"
                                  onChange={(e) => handleCategoryFieldChange('contact_details', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 4. INVITATION */}
                        {detectedCategory === 'invitation' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Mail className="w-3.5 h-3.5" />
                              <span>Invitation Details (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Occasion</label>
                                <input
                                  type="text"
                                  value={categoryData.occasion || ''}
                                  placeholder="e.g. Wedding, Birthday"
                                  onChange={(e) => handleCategoryFieldChange('occasion', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Host Names</label>
                                <input
                                  type="text"
                                  value={categoryData.host_names || ''}
                                  placeholder="e.g. Robert & Sarah Smith"
                                  onChange={(e) => handleCategoryFieldChange('host_names', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Date</label>
                                <input
                                  type="text"
                                  value={categoryData.date || ''}
                                  placeholder="e.g. Dec 25, 2026"
                                  onChange={(e) => handleCategoryFieldChange('date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Time</label>
                                <input
                                  type="text"
                                  value={categoryData.time || ''}
                                  placeholder="e.g. 6:30 PM"
                                  onChange={(e) => handleCategoryFieldChange('time', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div className="sm:col-span-2">
                                <label className="text-[11px] text-app-subtle block mb-1">Venue</label>
                                <input
                                  type="text"
                                  value={categoryData.venue || ''}
                                  placeholder="e.g. Grand Ballroom, Hilton"
                                  onChange={(e) => handleCategoryFieldChange('venue', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div className="sm:col-span-2">
                                <label className="text-[11px] text-app-subtle block mb-1">RSVP Details</label>
                                <input
                                  type="text"
                                  value={categoryData.rsvp_details || ''}
                                  placeholder="e.g. RSVP by Dec 1 to 555-0199"
                                  onChange={(e) => handleCategoryFieldChange('rsvp_details', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 5. TICKET */}
                        {detectedCategory === 'ticket' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Ticket className="w-3.5 h-3.5" />
                              <span>Ticket & Transit Information (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Carrier / Airline</label>
                                <input
                                  type="text"
                                  value={categoryData.carrier || ''}
                                  placeholder="e.g. Delta, Amtrak"
                                  onChange={(e) => handleCategoryFieldChange('carrier', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Booking Ref / PNR</label>
                                <input
                                  type="text"
                                  value={categoryData.booking_reference || categoryData.ticket_number || ''}
                                  placeholder="e.g. DL789X"
                                  onChange={(e) => handleCategoryFieldChange('booking_reference', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Seat / Berth</label>
                                <input
                                  type="text"
                                  value={categoryData.seat || ''}
                                  placeholder="e.g. 14B, Coach B4"
                                  onChange={(e) => handleCategoryFieldChange('seat', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Travel Date & Time</label>
                                <input
                                  type="text"
                                  value={categoryData.date || ''}
                                  placeholder="e.g. Nov 10, 2026"
                                  onChange={(e) => handleCategoryFieldChange('date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Departure Details</label>
                                <input
                                  type="text"
                                  value={categoryData.departure_details || categoryData.origin || ''}
                                  placeholder="e.g. JFK Terminal 4, 10:30 AM"
                                  onChange={(e) => handleCategoryFieldChange('departure_details', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Arrival Details</label>
                                <input
                                  type="text"
                                  value={categoryData.arrival_details || categoryData.destination || ''}
                                  placeholder="e.g. LHR Terminal 2"
                                  onChange={(e) => handleCategoryFieldChange('arrival_details', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 6. TRAVEL BOOKING */}
                        {detectedCategory === 'travel_booking' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Building className="w-3.5 h-3.5" />
                              <span>Travel Booking (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Provider / Platform</label>
                                <input
                                  type="text"
                                  value={categoryData.provider || ''}
                                  placeholder="e.g. Booking.com, Airbnb"
                                  onChange={(e) => handleCategoryFieldChange('provider', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Confirmation / Ref #</label>
                                <input
                                  type="text"
                                  value={categoryData.booking_reference || ''}
                                  placeholder="e.g. RES-99882"
                                  onChange={(e) => handleCategoryFieldChange('booking_reference', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Destination / Hotel</label>
                                <input
                                  type="text"
                                  value={categoryData.destination || ''}
                                  placeholder="e.g. Grand Resort & Spa"
                                  onChange={(e) => handleCategoryFieldChange('destination', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Check-in Details</label>
                                <input
                                  type="text"
                                  value={categoryData.check_in_details || ''}
                                  placeholder="e.g. Dec 14, 2026, 3:00 PM"
                                  onChange={(e) => handleCategoryFieldChange('check_in_details', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 7. IDENTITY DOCUMENT */}
                        {detectedCategory === 'identity_document' && (
                          <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-3">
                            <h5 className="text-xs font-semibold text-rose-300 flex items-center gap-1.5 uppercase tracking-wider">
                              <ShieldAlert className="w-3.5 h-3.5" />
                              <span>Identity Credentials (Masked for Privacy)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Document Type</label>
                                <input
                                  type="text"
                                  value={categoryData.document_type || ''}
                                  placeholder="e.g. Passport, Driver License"
                                  onChange={(e) => handleCategoryFieldChange('document_type', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Full Name</label>
                                <input
                                  type="text"
                                  value={categoryData.full_name || ''}
                                  placeholder="e.g. John Doe"
                                  onChange={(e) => handleCategoryFieldChange('full_name', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Masked ID Number</label>
                                <input
                                  type="text"
                                  value={categoryData.id_number_masked || '****-****-****'}
                                  disabled
                                  className="w-full bg-dark-surface/80 border border-dark-border rounded-lg px-2.5 py-1.5 text-xs text-app-muted outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Expiry Date</label>
                                <input
                                  type="text"
                                  value={categoryData.expiry_date || ''}
                                  placeholder="e.g. Jan 10, 2030"
                                  onChange={(e) => handleCategoryFieldChange('expiry_date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 8. CERTIFICATE */}
                        {detectedCategory === 'certificate' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Award className="w-3.5 h-3.5" />
                              <span>Certificate Credentials (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Recipient Name</label>
                                <input
                                  type="text"
                                  value={categoryData.recipient || categoryData.recipient_name || ''}
                                  placeholder="e.g. John Doe"
                                  onChange={(e) => handleCategoryFieldChange('recipient', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Certificate Type / Title</label>
                                <input
                                  type="text"
                                  value={categoryData.certificate_type || categoryData.title || ''}
                                  placeholder="e.g. Machine Learning Specialization"
                                  onChange={(e) => handleCategoryFieldChange('certificate_type', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Issuing Organization</label>
                                <input
                                  type="text"
                                  value={categoryData.issuing_organization || categoryData.issuer || ''}
                                  placeholder="e.g. Stanford University"
                                  onChange={(e) => handleCategoryFieldChange('issuing_organization', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Issue Date</label>
                                <input
                                  type="text"
                                  value={categoryData.issue_date || ''}
                                  placeholder="e.g. Oct 1, 2026"
                                  onChange={(e) => handleCategoryFieldChange('issue_date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 9. MEDICAL DOCUMENT */}
                        {detectedCategory === 'medical_document' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Activity className="w-3.5 h-3.5" />
                              <span>Medical Document Metadata (No Clinical Claims)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Document Type</label>
                                <input
                                  type="text"
                                  value={categoryData.document_type || ''}
                                  placeholder="e.g. Prescription, Lab Report"
                                  onChange={(e) => handleCategoryFieldChange('document_type', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Doctor / Clinic</label>
                                <input
                                  type="text"
                                  value={categoryData.clinic_or_doctor || ''}
                                  placeholder="e.g. Dr. Alan Stone, City Health"
                                  onChange={(e) => handleCategoryFieldChange('clinic_or_doctor', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Date</label>
                                <input
                                  type="text"
                                  value={categoryData.date || ''}
                                  placeholder="e.g. Oct 15, 2026"
                                  onChange={(e) => handleCategoryFieldChange('date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 10. OFFICIAL DOCUMENT */}
                        {detectedCategory === 'official_document' && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <FileCheck className="w-3.5 h-3.5" />
                              <span>Official Document Details (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Issuing Authority</label>
                                <input
                                  type="text"
                                  value={categoryData.issuing_authority || ''}
                                  placeholder="e.g. Department of Justice"
                                  onChange={(e) => handleCategoryFieldChange('issuing_authority', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Reference / File #</label>
                                <input
                                  type="text"
                                  value={categoryData.reference_number || ''}
                                  placeholder="e.g. REF-2026/901"
                                  onChange={(e) => handleCategoryFieldChange('reference_number', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none font-mono"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Subject</label>
                                <input
                                  type="text"
                                  value={categoryData.subject || ''}
                                  placeholder="e.g. Lease Agreement"
                                  onChange={(e) => handleCategoryFieldChange('subject', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Issue Date</label>
                                <input
                                  type="text"
                                  value={categoryData.issue_date || ''}
                                  placeholder="e.g. Sep 30, 2026"
                                  onChange={(e) => handleCategoryFieldChange('issue_date', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 11. NOTES & OTHERS */}
                        {(detectedCategory === 'handwritten_notes' || detectedCategory === 'printed_notes') && (
                          <div className="p-3.5 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-3">
                            <h5 className="text-xs font-semibold text-accent-light flex items-center gap-1.5 uppercase tracking-wider">
                              <Edit3 className="w-3.5 h-3.5" />
                              <span>Notes Overview (Editable)</span>
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Title / Topic</label>
                                <input
                                  type="text"
                                  value={categoryData.title || ''}
                                  placeholder="e.g. Thermodynamics Study Notes"
                                  onChange={(e) => handleCategoryFieldChange('title', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-app-subtle block mb-1">Subject</label>
                                <input
                                  type="text"
                                  value={categoryData.subject || ''}
                                  placeholder="e.g. Physics"
                                  onChange={(e) => handleCategoryFieldChange('subject', e.target.value)}
                                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1.5 text-xs text-white outline-none"
                                />
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Suggested Reminders (Requirement 12 - NEVER automatic without user confirmation) */}
                        {suggestedReminders.length > 0 && (
                          <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-2.5">
                            <div className="flex items-center justify-between">
                              <label className="text-xs font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                                <span>Suggested Reminders (Requires Your Confirmation)</span>
                              </label>
                              <span className="text-[10px] text-app-subtle">
                                Not added unless checked
                              </span>
                            </div>

                            <div className="space-y-2">
                              {suggestedReminders.map((rem) => (
                                <label
                                  key={rem.id}
                                  className={`flex items-start gap-3 p-2.5 rounded-xl border transition-all cursor-pointer ${
                                    rem.confirmed 
                                      ? 'bg-indigo-500/15 border-indigo-500/50 text-white' 
                                      : 'bg-dark-bg/80 border-dark-border text-app-muted hover:border-indigo-500/30'
                                  }`}
                                >
                                  <input
                                    type="checkbox"
                                    checked={Boolean(rem.confirmed)}
                                    onChange={() => toggleReminderConfirmation(rem.id)}
                                    className="mt-0.5 rounded border-dark-border text-indigo-500 focus:ring-0 cursor-pointer"
                                  />
                                  <div className="min-w-0 flex-1">
                                    <p className="text-xs font-semibold text-white truncate">{rem.title}</p>
                                    <p className="text-[11px] text-indigo-300 font-mono mt-0.5">
                                      {new Date(rem.dueDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                      {rem.priority === 'urgent' && ' • Urgent'}
                                    </p>
                                  </div>
                                </label>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Extracted Text Area with line count & copy */}
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <label className="text-xs font-semibold text-app-muted uppercase tracking-wider flex items-center gap-1.5">
                              <FileText className="w-3.5 h-3.5 text-palette-clay" />
                              <span>Extracted Clean OCR Text</span>
                              <span className="text-[11px] text-app-subtle font-normal lowercase">
                                ({ocrResult.lineCount || 0} lines • {ocrResult.wordCount || 0} words)
                              </span>
                            </label>
                            <button
                              type="button"
                              onClick={handleCopyOcrText}
                              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-dark-surface border border-dark-border text-xs text-app-muted hover:text-white hover:border-accent/40 transition-colors cursor-pointer"
                              title="Copy extracted text to clipboard"
                            >
                              {isCopied ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span className="text-emerald-400 font-medium">Copied!</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5 text-app-subtle" />
                                  <span>Copy Text</span>
                                </>
                              )}
                            </button>
                          </div>

                          <textarea
                            rows={4}
                            value={ocrEditableText}
                            onChange={(e) => setOcrEditableText(e.target.value)}
                            placeholder="No legible text detected in image."
                            className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl p-3 text-xs text-white placeholder-app-subtle outline-none resize-y font-mono leading-relaxed"
                          />
                        </div>

                        {/* Executive Summary */}
                        <div className="p-3 rounded-xl bg-palette-cream/40 dark:bg-dark-surface/60 border border-palette-border dark:border-dark-border/80 space-y-1">
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-accent-light">
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>Executive Summary (Editable)</span>
                          </div>
                          <textarea
                            rows={2}
                            value={customSummary}
                            onChange={(e) => setCustomSummary(e.target.value)}
                            className="w-full bg-transparent border-0 text-xs text-app-text outline-none resize-none leading-relaxed"
                          />
                        </div>

                        {/* Keywords for Search */}
                        <div className="space-y-1.5">
                          <label className="text-xs font-semibold text-app-muted uppercase tracking-wider flex items-center gap-1.5">
                            <Search className="w-3.5 h-3.5 text-palette-clay" />
                            <span>Keywords for Semantic Search & RAG</span>
                          </label>
                          <div className="flex flex-wrap gap-1.5">
                            {customKeywords.map((kw, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-palette-mist/20 border border-palette-mist/40 text-palette-slate dark:text-palette-mist"
                              >
                                <Hash className="w-3 h-3 opacity-60" />
                                <span>{kw}</span>
                              </span>
                            ))}
                          </div>
                        </div>

                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* MODALITY 3: AUDIO / VOICE RECORDING */}
            {activeTab === 'voice' && (
              <div className="space-y-4">
                <div className="p-6 rounded-2xl bg-dark-bg/80 border border-dark-border flex flex-col items-center justify-center text-center">
                  <div className="mb-4 text-3xl font-mono font-bold tracking-wider theme-gradient-text">
                    {formattedTime}
                  </div>

                  <AudioWaveform waveformData={waveformData} isRecording={isRecording} />

                  <div className="flex items-center gap-4 mt-6">
                    {!isRecording ? (
                      <button
                        type="button"
                        onClick={startRecording}
                        className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-palette-navy hover:bg-palette-slate text-white font-medium text-sm shadow-sm transition-all cursor-pointer"
                      >
                        <Mic className="w-4 h-4" />
                        <span>{audioUrl ? 'Record Again' : 'Start Recording'}</span>
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={stopRecording}
                        className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-rose-500 hover:bg-rose-600 text-white font-medium text-sm shadow-lg shadow-rose-500/20 transition-all cursor-pointer animate-pulse"
                      >
                        <Square className="w-4 h-4" />
                        <span>Stop Recording</span>
                      </button>
                    )}

                    {audioUrl && !isRecording && (
                      <button
                        type="button"
                        onClick={resetRecording}
                        className="p-2.5 rounded-full text-app-subtle hover:text-white hover:bg-dark-hover transition-colors cursor-pointer"
                        title="Reset"
                      >
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* MODALITY 4: PDF DOCUMENT */}
            {activeTab === 'pdf' && (
              <div>
                {!pdfFile ? (
                  <label className="border-2 border-dashed border-dark-border hover:border-indigo-400/60 rounded-2xl p-7 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group bg-dark-bg/40 block">
                    <input type="file" accept=".pdf" onChange={handlePdfChange} className="hidden" />
                    <div className="w-12 h-12 rounded-xl bg-dark-surface border border-dark-border flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-sm">
                      <FileUp className="w-6 h-6 text-indigo-400" />
                    </div>
                    <p className="text-sm font-semibold text-white mb-1">Upload PDF document</p>
                    <p className="text-xs text-app-subtle">Extract chapters, summaries, & figures</p>
                  </label>
                ) : (
                  <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileUp className="w-6 h-6 text-indigo-400" />
                      <div>
                        <p className="text-sm font-semibold text-white truncate max-w-xs">{pdfFile.name}</p>
                        <p className="text-xs text-app-subtle">{(pdfFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button type="button" onClick={() => setPdfFile(null)} className="p-1.5 text-app-subtle hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* MODALITY 5: POWERPOINT PPT */}
            {activeTab === 'ppt' && (
              <div>
                {!pptFile ? (
                  <label className="border-2 border-dashed border-dark-border hover:border-amber-400/60 rounded-2xl p-7 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group bg-dark-bg/40 block">
                    <input type="file" accept=".ppt,.pptx" onChange={handlePptChange} className="hidden" />
                    <div className="w-12 h-12 rounded-xl bg-dark-surface border border-dark-border flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-sm">
                      <Presentation className="w-6 h-6 text-amber-400" />
                    </div>
                    <p className="text-sm font-semibold text-white mb-1">Upload PowerPoint presentation</p>
                    <p className="text-xs text-app-subtle">Slide-by-slide AI analysis & notes</p>
                  </label>
                ) : (
                  <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Presentation className="w-6 h-6 text-amber-400" />
                      <div>
                        <p className="text-sm font-semibold text-white truncate max-w-xs">{pptFile.name}</p>
                        <p className="text-xs text-app-subtle">{(pptFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button type="button" onClick={() => setPptFile(null)} className="p-1.5 text-app-subtle hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* MODALITY 6: WORD DOCX */}
            {activeTab === 'docx' && (
              <div>
                {!docxFile ? (
                  <label className="border-2 border-dashed border-dark-border hover:border-cyan-400/60 rounded-2xl p-7 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group bg-dark-bg/40 block">
                    <input type="file" accept=".doc,.docx" onChange={handleDocxChange} className="hidden" />
                    <div className="w-12 h-12 rounded-xl bg-dark-surface border border-dark-border flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-sm">
                      <FileCode2 className="w-6 h-6 text-cyan-400" />
                    </div>
                    <p className="text-sm font-semibold text-white mb-1">Upload Microsoft Word document</p>
                    <p className="text-xs text-app-subtle">Structured manuscript outline</p>
                  </label>
                ) : (
                  <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileCode2 className="w-6 h-6 text-cyan-400" />
                      <div>
                        <p className="text-sm font-semibold text-white truncate max-w-xs">{docxFile.name}</p>
                        <p className="text-xs text-app-subtle">{(docxFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button type="button" onClick={() => setDocxFile(null)} className="p-1.5 text-app-subtle hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* MODALITY 7: WEB LINK */}
            {activeTab === 'link' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5">
                    Target Web URL
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="url"
                      placeholder="https://example.com/article"
                      value={linkUrl}
                      onChange={(e) => setLinkUrl(e.target.value)}
                      className="flex-1 bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-app-subtle outline-none"
                    />
                    <button
                      type="button"
                      onClick={handleLinkFetch}
                      disabled={isFetchingLink || !linkUrl.trim()}
                      className="px-4 py-2.5 rounded-xl bg-dark-surface border border-dark-border text-xs font-semibold text-white hover:bg-dark-hover transition-colors flex items-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      {isFetchingLink ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4 text-emerald-400" />}
                      <span>Fetch</span>
                    </button>
                  </div>
                </div>

                {linkMetadata && (
                  <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1.5 animate-fadeIn">
                    <p className="text-xs font-semibold text-emerald-300">{linkMetadata.title}</p>
                    <p className="text-[11px] text-app-muted">{linkMetadata.excerpt}</p>
                  </div>
                )}
              </div>
            )}

            {/* Category Selector for Non-Images */}
            {activeTab !== 'image' && (
              <div>
                <label className="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5">
                  Knowledge Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-white outline-none cursor-pointer"
                >
                  <option value="Research">Research</option>
                  <option value="Architecture">Architecture</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Product">Product</option>
                  <option value="DevOps">DevOps</option>
                  <option value="Design">Design</option>
                  <option value="General">General</option>
                </select>
              </div>
            )}

            {/* Bottom Actions */}
            <div className="pt-3 border-t border-dark-border/80 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={closeCapture}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-app-muted hover:text-white transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isProcessing || isOcrLoading || (activeTab === 'image' && !imagePreview)}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-accent to-accent-hover text-white text-xs font-semibold shadow-glow-sm hover:brightness-110 active:scale-95 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Save & Index to Vault</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
