import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import EvaluationPage from '../pages/EvaluationPage'
import { evaluationApi } from '../services/api'

vi.mock('../services/api', () => ({
  evaluationApi: {
    get: vi.fn(),
    run: vi.fn(),
  },
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock recharts responsive container for jsdom
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="recharts-container">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  RadarChart: ({ children }: any) => <div data-testid="radar-chart">{children}</div>,
  Radar: () => <div />,
  PolarGrid: () => <div />,
  PolarAngleAxis: () => <div />,
}))

describe('EvaluationPage Component', () => {
  const mockEvalReport = {
    baseline: {
      system_type: 'baseline_static_rules',
      precision: 0.309,
      recall: 0.446,
      f1_score: 0.386,
      acceptance_rate: 0.469,
      avg_response_time_ms: 12.0,
      evidence_coverage: 0.0,
      false_positive_rate: 0.691,
      false_negative_rate: 0.554,
      failure_rate: 0.25,
      is_synthetic: false,
    },
    ai_rag: {
      system_type: 'ai_rag_pipeline',
      precision: 0.842,
      recall: 0.680,
      f1_score: 0.750,
      acceptance_rate: 0.810,
      avg_response_time_ms: 28.5,
      evidence_coverage: 1.0,
      false_positive_rate: 0.158,
      false_negative_rate: 0.320,
      failure_rate: 0.0,
      is_synthetic: false,
    },
    improvement: {
      f1_score: 94.3,
      precision: 172.5,
      recall: 52.5,
      acceptance_rate: 72.7,
      evidence_coverage: 100.0,
      failure_rate: 100.0,
    },
    scenarios_evaluated: 12,
    notes: 'Empirical benchmark against 12 enterprise ground truth scenarios.',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(evaluationApi.get).mockReturnValue(new Promise(() => {}))
    render(<EvaluationPage />)
    expect(screen.getByText(/Loading evaluation benchmark data/i)).toBeInTheDocument()
  })

  it('renders verified empirical benchmark results with ground truth badge', async () => {
    vi.mocked(evaluationApi.get).mockResolvedValue(mockEvalReport)
    render(<EvaluationPage />)

    await waitFor(() => {
      expect(screen.getByText('Empirical Evaluation & Benchmark Engine')).toBeInTheDocument()
    })

    // Ground truth badge
    expect(screen.getByText('Verified Empirical Benchmark Results')).toBeInTheDocument()
    expect(screen.getByText('Ground Truth Evaluated')).toBeInTheDocument()

    // Key metrics
    expect(screen.getAllByText('+94.3%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('84.2%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('81.0%').length).toBeGreaterThanOrEqual(1)

    // Action button
    expect(screen.getByRole('button', { name: /Run Live Benchmark/i })).toBeInTheDocument()
  })

  it('displays comprehensive operational comparison table', async () => {
    vi.mocked(evaluationApi.get).mockResolvedValue(mockEvalReport)
    render(<EvaluationPage />)

    await waitFor(() => {
      expect(screen.getByText('Comprehensive Operational Benchmark (Baseline vs. AI+RAG)')).toBeInTheDocument()
    })

    // Check rows in table
    expect(screen.getByText('Precision')).toBeInTheDocument()
    expect(screen.getByText('Recall')).toBeInTheDocument()
    expect(screen.getByText('F1 Score')).toBeInTheDocument()
    expect(screen.getByText('User Acceptance Rate')).toBeInTheDocument()
    expect(screen.getByText('Evidence Citation Coverage')).toBeInTheDocument()
    expect(screen.getByText('False Positive Rate')).toBeInTheDocument()
  })
})
