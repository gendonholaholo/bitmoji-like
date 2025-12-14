import React from 'react';
import { AlertTriangle, Shield, CheckCircle, Search, Heart, Beaker } from 'lucide-react';
import SemiCircularGauge from './SemiCircularGauge';
import ImageComparisonSlider from './ImageComparisonSlider';
import './ConcernDetail.css';

// Marker color legend configuration
// UPDATED: Warna dioptimalkan untuk UV tint cyan/teal (sinkron dengan backend)
// Menggunakan pink/coral/magenta yang kontras dengan background cyan
const MARKER_LEGENDS = {
    acne: [
        { color: '#ffc8b4', label: 'Bekas jerawat' },      // Light peach (mild)
        { color: '#ff8ca0', label: 'Area meradang' },      // Salmon pink (moderate)
        { color: '#ff5064', label: 'Jerawat aktif' },      // Coral red (severe)
    ],
    pore: [
        { color: '#78dcff', label: 'Pori tersumbat' },     // Light cyan (mild)
        { color: '#ffb48c', label: 'Pori membesar' },      // Peach (moderate)
        { color: '#ff6482', label: 'Area berminyak' },     // Coral pink (severe)
    ],
    wrinkle: [
        { color: '#64c8ff', label: 'Garis halus' },        // Sky blue (mild)
        { color: '#c864dc', label: 'Kerutan sedang' },     // Magenta (moderate)
        { color: '#ff5078', label: 'Kerutan dalam' },      // Hot pink (severe)
    ],
    age_spot: [
        { color: '#8cdcff', label: 'Titik ringan' },       // Light cyan (mild)
        { color: '#ffb496', label: 'Bintik-bintik' },      // Peach (moderate-mild)
        { color: '#ff8282', label: 'Melasma' },            // Salmon (moderate)
        { color: '#ff5a78', label: 'Bintik dewasa' },      // Coral pink (severe)
    ],
    dark_circle_v2: [
        { color: '#8296ff', label: 'Vaskular' },           // Periwinkle (mild)
        { color: '#b464c8', label: 'Pigmentasi' },         // Orchid (moderate)
        { color: '#dc50a0', label: 'Struktural' },         // Deep pink (severe)
    ],
    oiliness: [
        { color: '#ffb478', label: 'Zona berminyak' },     // Light coral (mild)
        { color: '#ff7896', label: 'Sangat berminyak' },   // Pink/coral (severe)
    ],
    redness: [
        { color: '#ff96aa', label: 'Kemerahan ringan' },   // Light pink (mild)
        { color: '#ff6482', label: 'Kemerahan sedang' },   // Coral (moderate)
        { color: '#ff3c64', label: 'Kemerahan tinggi' },   // Hot pink/red (severe)
    ],
    firmness: [
        { color: '#64dcf0', label: 'Elastisitas baik' },   // Aqua (mild)
        { color: '#ffb48c', label: 'Penurunan ringan' },   // Peach (moderate)
        { color: '#ff648c', label: 'Perlu perhatian' },    // Coral pink (severe)
    ],
    radiance: [
        { color: '#fff0b4', label: 'Area cerah' },         // Cream yellow (mild)
        { color: '#c8b4c8', label: 'Kusam' },              // Lavender gray (moderate)
        { color: '#b48cb4', label: 'Sangat kusam' },       // Dusty pink (severe)
    ],
};

/**
 * Severity thresholds synchronized with backend (landmark_service.py)
 * Based on dermatological literature:
 * - Glogau Scale (wrinkles)
 * - Global Acne Grading System
 * - Baumann Skin Typing System (oiliness)
 *
 * Higher score = better skin condition = milder severity
 */
const SEVERITY_THRESHOLDS = {
    2: [50],           // 2 levels: >= 50 = level 0 (mild), < 50 = level 1 (severe)
    3: [66, 33],       // 3 levels: >= 66 = 0, 33-65 = 1, < 33 = 2
    4: [75, 50, 25],   // 4 levels: >= 75 = 0, 50-74 = 1, 25-49 = 2, < 25 = 3
};

/**
 * Get active severity level index based on score
 * @param {number} score - UI score from YouCam API (0-100, higher = better)
 * @param {number} numLevels - Number of severity levels for this concern
 * @returns {number} Active level index (0 = mildest, numLevels-1 = most severe)
 */
const getActiveLegendIndex = (score, numLevels) => {
    if (!SEVERITY_THRESHOLDS[numLevels]) {
        return 0; // Default to first level if unknown
    }

    const thresholds = SEVERITY_THRESHOLDS[numLevels];
    for (let i = 0; i < thresholds.length; i++) {
        if (score >= thresholds[i]) {
            return i;
        }
    }
    return numLevels - 1; // Most severe level
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
    landmarkStatus,
}) {
    const analysis = analysisText || DEFAULT_ANALYSIS;
    const legends = MARKER_LEGENDS[concern.key] || MARKER_LEGENDS.pore;

    // Calculate active legend index based on score
    const activeLegendIndex = getActiveLegendIndex(score || 0, legends.length);
    
    // Status landmark untuk transparency
    const getLandmarkStatusMessage = () => {
        if (!landmarkStatus) return null;
        
        if (landmarkStatus.landmark_status === 'failed') {
            return {
                type: 'warning',
                message: landmarkStatus.landmark_error || 'Deteksi landmark gagal',
                detail: landmarkStatus.fallback_used 
                    ? 'Menggunakan visualisasi mask dasar' 
                    : 'Area deteksi mungkin tidak akurat'
            };
        }
        if (landmarkStatus.landmark_status === 'partial') {
            return {
                type: 'info',
                message: 'Deteksi landmark sebagian',
                detail: `Confidence: ${Math.round(landmarkStatus.confidence * 100)}%`
            };
        }
        return null;
    };
    
    const statusMessage = getLandmarkStatusMessage();

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

                        {/* Legend overlay with active/inactive states */}
                        <div className="image-legend">
                            {legends.map((item, index) => {
                                const isActive = index === activeLegendIndex;
                                return (
                                    <div
                                        key={index}
                                        className={`legend-item ${isActive ? 'legend-active' : 'legend-inactive'}`}
                                    >
                                        <span
                                            className="legend-color"
                                            style={{ backgroundColor: item.color }}
                                        />
                                        <span className="legend-label">{item.label}</span>
                                        {isActive && <span className="legend-indicator">●</span>}
                                    </div>
                                );
                            })}
                        </div>
                        
                        {/* Landmark status indicator (transparency) */}
                        {statusMessage && (
                            <div className={`landmark-status ${statusMessage.type}`}>
                                <span className="status-icon">
                                    {statusMessage.type === 'warning' ? '⚠️' : 'ℹ️'}
                                </span>
                                <div className="status-text">
                                    <span className="status-message">{statusMessage.message}</span>
                                    <span className="status-detail">{statusMessage.detail}</span>
                                </div>
                            </div>
                        )}
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
