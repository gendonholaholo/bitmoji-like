import React from 'react';
import { Activity } from 'lucide-react';
import './ResultsDashboard.css';

export default function ResultsDashboard({ results }) {
    if (!results || !results.scores) {
        return null;
    }

    const { scores, composite_image } = results;

    // Get score color based on value
    const getScoreColor = (score) => {
        if (score >= 75) return 'score-excellent';
        if (score >= 50) return 'score-good';
        return 'score-attention';
    };

    // Get top 3 worst concerns (lowest scores)
    const getTopWorstConcerns = () => {
        const allConcerns = [
            { name: 'Wrinkle', data: scores.wrinkle || scores.hd_wrinkle },
            { name: 'Acne', data: scores.acne || scores.hd_acne },
            { name: 'Pore', data: scores.pore || scores.hd_pore },
            { name: 'Texture', data: scores.texture || scores.hd_texture },
            { name: 'Age Spot', data: scores.age_spot || scores.hd_age_spot },
            { name: 'Eye Bag', data: scores.eye_bag || scores.hd_eye_bag },
            { name: 'Dark Circle', data: scores.dark_circle_v2 || scores.hd_dark_circle },
            { name: 'Droopy Lower Eyelid', data: scores.droopy_lower_eyelid || scores.hd_droopy_lower_eyelid },
            { name: 'Droopy Upper Eyelid', data: scores.droopy_upper_eyelid || scores.hd_droopy_upper_eyelid },
            { name: 'Redness', data: scores.redness || scores.hd_redness },
            { name: 'Oiliness', data: scores.oiliness || scores.hd_oiliness },
            { name: 'Radiance', data: scores.radiance || scores.hd_radiance },
            { name: 'Moisture', data: scores.moisture || scores.hd_moisture },
            { name: 'Firmness', data: scores.firmness || scores.hd_firmness },
        ];

        // Extract scores and filter valid ones
        const concernsWithScores = allConcerns
            .map(concern => {
                let score = null;

                // Handle both simple scores and subcategory scores (whole)
                if (concern.data) {
                    if (concern.data.ui_score !== undefined) {
                        score = concern.data.ui_score;
                    } else if (concern.data.whole && concern.data.whole.ui_score !== undefined) {
                        score = concern.data.whole.ui_score;
                    } else if (concern.data.score !== undefined) {
                        score = concern.data.score;
                    }
                }

                return { ...concern, score };
            })
            .filter(c => c.score !== null);

        // Sort by score (lowest first) and take top 3 worst
        return concernsWithScores
            .sort((a, b) => a.score - b.score)
            .slice(0, 3);
    };

    const topWorstConcerns = getTopWorstConcerns();

    return (
        <div className="results-container">
            {/* Purple gradient background */}
            <div className="gradient-background" />

            <div className="results-content">
                {/* Header title */}
                <h1 className="results-title">Here's your comprehensive skin analysis</h1>

                {/* Top cards: Overall Score + Skin Age */}
                <div className="header-cards">
                    <div className="header-card glass-card">
                        <h2 className="header-card-title">Overall Skin Score</h2>
                        <div className="header-card-value">
                            {Math.round(scores.all.score)}
                        </div>
                        <p className="header-card-subtitle">Out of 100</p>
                    </div>

                    <div className="header-card glass-card">
                        <h2 className="header-card-title">Skin Age</h2>
                        <div className="header-card-value skin-age">
                            {scores.skin_age}
                        </div>
                        <p className="header-card-subtitle">Years</p>
                    </div>
                </div>

                {/* MAIN FOCUS: Large composite visualization image */}
                {composite_image && (
                    <div className="main-visual">
                        <img
                            src={`data:image/jpeg;base64,${composite_image}`}
                            alt="Skin Analysis Visualization"
                            className="large-composite"
                        />
                    </div>
                )}

                {/* Top 3 worst concerns - mini cards */}
                <div className="mini-concerns">
                    {topWorstConcerns.map((concern, index) => (
                        <div key={index} className="mini-concern-card glass-card">
                            <div className="mini-concern-label">
                                <Activity size={16} />
                                <span>{concern.name}</span>
                            </div>
                            <div className={`mini-concern-score ${getScoreColor(concern.score)}`}>
                                {Math.round(concern.score)}
                            </div>
                            <div className="mini-concern-bar-container">
                                <div
                                    className={`mini-concern-bar ${getScoreColor(concern.score)}`}
                                    style={{ width: `${concern.score}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Score legend */}
                <div className="score-guide glass-card">
                    <h3 className="guide-title">Score Guide</h3>
                    <div className="guide-items">
                        <div className="guide-item">
                            <div className="guide-color score-excellent" />
                            <span>75-100: Excellent</span>
                        </div>
                        <div className="guide-item">
                            <div className="guide-color score-good" />
                            <span>50-74: Good</span>
                        </div>
                        <div className="guide-item">
                            <div className="guide-color score-attention" />
                            <span>0-49: Needs Attention</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
