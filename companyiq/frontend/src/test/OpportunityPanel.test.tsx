import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { OpportunityPanel } from '../components/OpportunityPanel'

// Mock toast and api
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

vi.mock('../services/api', () => ({
  feedbackApi: {
    submit: vi.fn().mockResolvedValue({ status: 'ok' }),
  },
}))

describe('OpportunityPanel Component', () => {
  const mockOpportunities = [
    {
      id: 'opp-12345',
      title: 'Battery Predictive Health Analytics Platform',
      description: 'AI-driven telemetry monitoring cell temperatures and state of charge.',
      what: 'Cloud-based battery digital twin deployed across electric fleet.',
      why: 'Reduces warranty replacement costs by 22% and prevents thermal runaway.',
      limitations: 'Requires integration with onboard CAN bus telematics.',
      confidence: { value: 0.92, label: 'HIGH' },
      evidence: [
        {
          chunk_id: 'chk_tata_ev_01',
          document_name: 'Tata_Motors_Annual_Report_2024.pdf',
          source_type: 'annual_report',
          title: 'Tata Motors Annual Report',
          snippet: 'Scaling electric mobility with continuous telemetry and warranty risk containment.',
          relevance_score: 0.94,
        },
      ],
      score_breakdown: {
        business_relevance: 92.0,
        recent_activity: 85.0,
        product_fit: 90.0,
        historical_similarity: 78.0,
        evidence_confidence: 95.0,
        overall: 88.5,
        level: 'HIGH',
      },
    },
  ]

  it('renders opportunity title and overall score', () => {
    render(<OpportunityPanel opportunities={mockOpportunities} />)

    expect(screen.getByText('Battery Predictive Health Analytics Platform')).toBeInTheDocument()
    expect(screen.getByText('89')).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
  })

  it('displays empty state when no opportunities are provided', () => {
    render(<OpportunityPanel opportunities={[]} />)
    expect(screen.getByText('No opportunities identified yet')).toBeInTheDocument()
  })

  it('expands details to show WHAT, WHY, and verifiable Chunk ID citation', () => {
    render(<OpportunityPanel opportunities={mockOpportunities} />)

    // Click chevron to expand card
    const expandBtn = screen.getByRole('button', { name: '' })
    fireEvent.click(expandBtn)

    // Check WHAT and WHY
    expect(screen.getByText('Cloud-based battery digital twin deployed across electric fleet.')).toBeInTheDocument()
    expect(screen.getByText('Reduces warranty replacement costs by 22% and prevents thermal runaway.')).toBeInTheDocument()

    // Check Verifiable Chunk Citation
    expect(screen.getByText('Chunk #chk_tata_ev_01')).toBeInTheDocument()
    expect(screen.getByText('Tata_Motors_Annual_Report_2024.pdf')).toBeInTheDocument()
    expect(screen.getByText('94% semantic match')).toBeInTheDocument()
  })

  it('renders human-in-the-loop feedback buttons (Accept, Reject, Need Evidence)', () => {
    render(<OpportunityPanel opportunities={mockOpportunities} />)

    const expandBtn = screen.getByRole('button', { name: '' })
    fireEvent.click(expandBtn)

    expect(screen.getByText('Accept')).toBeInTheDocument()
    expect(screen.getByText('Reject')).toBeInTheDocument()
    expect(screen.getByText('Need Evidence')).toBeInTheDocument()
  })
})
