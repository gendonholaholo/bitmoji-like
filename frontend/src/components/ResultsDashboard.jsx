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

    // Render a simple score card (for individual concerns)
    const renderConcernCard = (label, scoreData) => {
        if (!scoreData) return null;

        const score = scoreData.ui_score || scoreData.score;

        return (
            <div className="concern-card glass-card">
                <div className="concern-header">
                    <Activity size={20} className="concern-icon" />
                    <span className="concern-label">{label}</span>
                </div>
                <div className={`concern-score ${getScoreColor(score)}`}>
                    {Math.round(score)}
                </div>
                <div className="concern-bar-container">
                    <div
                        className={`concern-bar ${getScoreColor(score)}`}
                        style={{ width: `${score}%` }}
                    />
                </div>
            </div>
        );
    };

    // Render subcategory (with whole score)
    const renderSubcategoryConcern = (label, subcategoryData) => {
        if (!subcategoryData || !subcategoryData.whole) return null;
        return renderConcernCard(label, subcategoryData.whole);
    };

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

                {/* Composite visualization image */}
                {composite_image && (
                    <div className="composite-section">
                        <img
                            src={`data:image/jpeg;base64,${composite_image}`}
                            alt="Skin Analysis Visualization"
                            className="composite-image"
                        />
                    </div>
                )}

                {/* Individual concern cards */}
                <div className="concerns-grid">
                    {/* Render all available concerns */}
                    {renderSubcategoryConcern('Wrinkle', scores.wrinkle || scores.hd_wrinkle)}
                    {renderSubcategoryConcern('Acne', scores.acne || scores.hd_acne)}
                    {renderSubcategoryConcern('Pore', scores.pore || scores.hd_pore)}
                    {renderSubcategoryConcern('Texture', scores.texture || scores.hd_texture)}
                    {renderConcernCard('Age Spot', scores.age_spot || scores.hd_age_spot)}
                    {renderConcernCard('Eye Bag', scores.eye_bag || scores.hd_eye_bag)}
                    {renderConcernCard('Dark Circle', scores.dark_circle_v2 || scores.hd_dark_circle)}
                    {renderConcernCard('Droopy Lower Eyelid', scores.droopy_lower_eyelid || scores.hd_droopy_lower_eyelid)}
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
