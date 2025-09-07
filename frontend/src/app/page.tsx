'use client';

import { useState, useRef, useEffect } from 'react';
import { Upload, Play, CheckCircle, Clock, AlertCircle, FileText, Users, TrendingUp } from 'lucide-react';

interface Task {
  user_id: string;
  opportunity_type: string;
  reasoning: string;
  recommended_action: string;
}

interface AnalysisResponse {
  success: boolean;
  message: string;
  tasks: Task[];
  analysis_time: string;
  total_events: number;
}

interface AgentStatus {
  status: string;
  message: string;
  timestamp: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    status: 'idle',
    message: 'Agent ready',
    timestamp: new Date().toISOString()
  });
  const [useSampleData, setUseSampleData] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch agent status on component mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8001/status');
        const status = await response.json();
        setAgentStatus(status);
      } catch (error) {
        console.error('Failed to fetch agent status:', error);
      }
    };
    
    fetchStatus();
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/json') {
      setFile(selectedFile);
      setUseSampleData(false);
    } else {
      alert('Please select a valid JSON file');
    }
  };


  const analyzeEvents = async () => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAgentStatus({
      status: 'analyzing',
      message: 'Processing events...',
      timestamp: new Date().toISOString()
    });

    try {
      const requestBody: any = {};
      
      if (useSampleData) {
        requestBody.use_sample_data = true;
      } else if (file) {
        // First upload the file
        const formData = new FormData();
        formData.append('file', file);

        const uploadResponse = await fetch('http://localhost:8001/upload', {
          method: 'POST',
          body: formData,
        });

        const uploadResult = await uploadResponse.json();
        if (!uploadResult.success) {
          throw new Error(uploadResult.message || 'Upload failed');
        }
        
        requestBody.events_file_path = uploadResult.file_path;
      } else {
        alert('Please select a file or use sample data');
        setIsAnalyzing(false);
        return;
      }

      const response = await fetch('http://localhost:8001/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result: AnalysisResponse = await response.json();
      setAnalysisResult(result);
      setAgentStatus({
        status: 'completed',
        message: `Analysis completed. Found ${result.tasks.length} opportunities.`,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Analysis error:', error);
      setAgentStatus({
        status: 'error',
        message: `Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString()
      });
      alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'analyzing':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'analyzing':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <div className="ml-3">
                <h1 className="text-2xl font-bold text-gray-900">Upsell Agent</h1>
                <p className="text-sm text-gray-500">AI-powered upsell opportunity analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(agentStatus.status)}`}>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(agentStatus.status)}
                  <span>{agentStatus.message}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Controls */}
          <div className="space-y-6">
            {/* File Upload Section */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Events Data</h2>
              
              <div className="space-y-4">
                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    PostHog Events File
                  </label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                    <div className="space-y-1 text-center">
                      <Upload className="mx-auto h-12 w-12 text-gray-400" />
                      <div className="flex text-sm text-gray-600">
                        <label
                          htmlFor="file-upload"
                          className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                        >
                          <span>Upload a JSON file</span>
                          <input
                            ref={fileInputRef}
                            id="file-upload"
                            name="file-upload"
                            type="file"
                            className="sr-only"
                            accept=".json"
                            onChange={handleFileUpload}
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">JSON files only</p>
                    </div>
                  </div>
                  {file && (
                    <div className="mt-2 flex items-center text-sm text-gray-600">
                      <FileText className="w-4 h-4 mr-2" />
                      {file.name}
                    </div>
                  )}
                </div>

                {/* Sample Data Option */}
                <div className="flex items-center">
                  <input
                    id="use-sample"
                    type="checkbox"
                    checked={useSampleData}
                    onChange={(e) => {
                      setUseSampleData(e.target.checked);
                      if (e.target.checked) {
                        setFile(null);
                        if (fileInputRef.current) {
                          fileInputRef.current.value = '';
                        }
                      }
                    }}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="use-sample" className="ml-2 block text-sm text-gray-900">
                    Use sample data (1000+ events)
                  </label>
                </div>

                {/* Analyze Button */}
                <button
                  onClick={analyzeEvents}
                  disabled={isAnalyzing || (!file && !useSampleData)}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAnalyzing ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Analyze Events
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Analysis Stats */}
            {analysisResult && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{analysisResult.total_events}</div>
                    <div className="text-sm text-gray-500">Total Events</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{analysisResult.tasks.length}</div>
                    <div className="text-sm text-gray-500">Opportunities Found</div>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <div className="text-sm text-gray-500">Analysis Time: {analysisResult.analysis_time}</div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Agent Output */}
          <div className="space-y-6">
            {/* Agent Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Agent Status</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Status</span>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agentStatus.status)}`}>
                    {agentStatus.status}
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  {agentStatus.message}
                </div>
                <div className="text-xs text-gray-500">
                  Last updated: {new Date(agentStatus.timestamp).toLocaleString()}
                </div>
              </div>
            </div>

            {/* Tasks Output */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upsell Opportunities</h2>
              
              {analysisResult ? (
                <div className="space-y-4">
                  {analysisResult.tasks.map((task, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Users className="w-4 h-4 text-blue-500" />
                          <span className="font-medium text-gray-900">{task.user_id}</span>
                        </div>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                          {task.opportunity_type}
                        </span>
                      </div>
                      
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium text-gray-700">Reasoning:</span>
                          <p className="text-sm text-gray-600 mt-1">{task.reasoning}</p>
                        </div>
                        
                        <div>
                          <span className="text-sm font-medium text-gray-700">Recommended Action:</span>
                          <p className="text-sm text-gray-600 mt-1">{task.recommended_action}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No analysis results yet. Upload events data and click "Analyze Events" to get started.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}