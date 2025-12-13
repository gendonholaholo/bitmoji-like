import React from 'react';
import { AlertTriangle, Shield, CheckCircle, Search, Heart, Beaker } from 'lucide-react';
import SemiCircularGauge from './SemiCircularGauge';
import ImageComparisonSlider from './ImageComparisonSlider';
import './ConcernDetail.css';

// Marker color legend configuration
const MARKER_LEGENDS = {
    acne: [
        { color: '#ff3b30', label: 'Jerawat aktif' },
        { color: '#ff9500', label: 'Area meradang' },
        { color: '#ffcc00', label: 'Bekas jerawat' },
    ],
    pore: [
        { color: '#00d4ff', label: 'Pori tersumbat' },
        { color: '#ff9500', label: 'Pori membesar' },
        { color: '#ffcc00', label: 'Area berminyak' },
    ],
    wrinkle: [
        { color: '#00d4ff', label: 'Garis halus' },
        { color: '#a855f7', label: 'Kerutan sedang' },
        { color: '#ef4444', label: 'Kerutan dalam' },
    ],
    age_spot: [
        { color: '#00d4ff', label: 'Titik lain' },
        { color: '#ff9500', label: 'Bintik-bintik' },
        { color: '#8b5a2b', label: 'Melasma' },
        { color: '#a0522d', label: 'Bintik-bintik dewasa' },
    ],
    dark_circle_v2: [
        { color: '#5c5cff', label: 'Vaskular' },
        { color: '#8b4513', label: 'Pigmentasi' },
        { color: '#808080', label: 'Struktural' },
    ],
    oiliness: [
        { color: '#ffcc00', label: 'Zona berminyak' },
        { color: '#ff9500', label: 'Sangat berminyak' },
    ],
    redness: [
        { color: '#ff6b6b', label: 'Kemerahan ringan' },
        { color: '#ef4444', label: 'Kemerahan sedang' },
        { color: '#dc2626', label: 'Kemerahan tinggi' },
    ],
    firmness: [
        { color: '#00d4ff', label: 'Elastisitas baik' },
        { color: '#f59e0b', label: 'Penurunan ringan' },
        { color: '#ef4444', label: 'Perlu perhatian' },
    ],
    radiance: [
        { color: '#ffd700', label: 'Area cerah' },
        { color: '#c0c0c0', label: 'Kusam' },
        { color: '#808080', label: 'Sangat kusam' },
    ],
};

// Default analysis text if not provided
const DEFAULT_ANALYSIS = {
    quantitative: 'Analisis kuantitatif tidak tersedia.',
    precautions: 'Informasi kewaspadaan tidak tersedia.',
    recommendations: [],
    root_cause: 'Informasi penyebab tidak tersedia.',
    lifestyle_tips: [],
    product_ingredients: [],
};

export default function ConcernDetail({
    concern,
    score,
    originalImage,
    concernOverlay,
    compositeImage,
    analysisText,
}) {
    const analysis = analysisText || DEFAULT_ANALYSIS;
    const legends = MARKER_LEGENDS[concern.key] || MARKER_LEGENDS.pore;

    // Get the best overlay image for this specific concern
    const getOverlayImage = () => {
        // Priority: concern-specific overlay > composite > original
        if (concernOverlay) return concernOverlay;
        if (compositeImage) return compositeImage;
        return originalImage;
    };

    return (
        <div className="concern-detail">
            {/* Image section with comparison slider */}
            <div className="concern-image-section">
                {originalImage && (
                    <div className="concern-image-wrapper">
                        <ImageComparisonSlider
                            beforeImage={originalImage}
                            afterImage={getOverlayImage()}
                            beforeLabel="Original"
                            afterLabel={concern.label}
                        />

                        {/* Legend overlay */}
                        <div className="image-legend">
                            {legends.map((item, index) => (
                                <div key={index} className="legend-item">
                                    <span
                                        className="legend-color"
                                        style={{ backgroundColor: item.color }}
                                    />
                                    <span className="legend-label">{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Score gauge section */}
            <div className="concern-score-section glass-card">
                <h3 className="section-header">Indeks Umum kulit wajah penuh</h3>
                <SemiCircularGauge
                    score={score || 0}
                    label={concern.label}
                    animated={true}
                />
            </div>

            {/* Quantitative Analysis */}
            <div className="analysis-section glass-card">
                <h3 className="section-header">
                    <span className="section-marker">|</span>
                    Analisis Kuantitatif
                </h3>
                <p className="analysis-text">{analysis.quantitative}</p>
            </div>

            {/* Precautions */}
            <div className="analysis-section glass-card">
                <h3 className="section-header">
                    <span className="section-marker">|</span>
                    Kewaspadaan
                </h3>
                <div className="precaution-content">
                    <AlertTriangle size={20} className="precaution-icon" />
                    <p className="analysis-text">{analysis.precautions}</p>
                </div>
            </div>

            {/* Recommendations */}
            <div className="analysis-section glass-card">
                <h3 className="section-header">
                    <span className="section-marker">|</span>
                    Skema yang Direkomendasikan
                </h3>
                {analysis.recommendations && analysis.recommendations.length > 0 ? (
                    <div className="recommendations-list">
                        {analysis.recommendations.map((rec, index) => (
                            <div key={index} className="recommendation-item">
                                <CheckCircle size={16} className="rec-icon" />
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="no-recommendations">
                        <Shield size={24} />
                        <p>Tidak ada skema yang direkomendasikan</p>
                    </div>
                )}
            </div>

            {/* Root Cause */}
            {analysis.root_cause && analysis.root_cause !== 'Analisis AI tidak tersedia.' && (
                <div className="analysis-section glass-card">
                    <h3 className="section-header">
                        <span className="section-marker root-cause">|</span>
                        Penyebab Utama
                    </h3>
                    <div className="root-cause-content">
                        <Search size={20} className="root-cause-icon" />
                        <p className="analysis-text">{analysis.root_cause}</p>
                    </div>
                </div>
            )}

            {/* Lifestyle Tips */}
            {analysis.lifestyle_tips && analysis.lifestyle_tips.length > 0 && (
                <div className="analysis-section glass-card">
                    <h3 className="section-header">
                        <span className="section-marker lifestyle">|</span>
                        Tips Gaya Hidup
                    </h3>
                    <div className="tips-list">
                        {analysis.lifestyle_tips.map((tip, index) => (
                            <div key={index} className="tip-item">
                                <Heart size={16} className="tip-icon" />
                                <span>{tip}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Product Ingredients */}
            {analysis.product_ingredients && analysis.product_ingredients.length > 0 && (
                <div className="analysis-section glass-card">
                    <h3 className="section-header">
                        <span className="section-marker ingredients">|</span>
                        Bahan Aktif yang Disarankan
                    </h3>
                    <div className="ingredients-list">
                        {analysis.product_ingredients.map((ingredient, index) => (
                            <div key={index} className="ingredient-item">
                                <Beaker size={16} className="ingredient-icon" />
                                <span>{ingredient}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
