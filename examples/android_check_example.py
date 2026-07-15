"""
Android Integration Example
Shows how to integrate the trust assessment into an Android app.

This is a Kotlin example for the Android side.
"""

KOTLIN_EXAMPLE = '''
// Android/Kotlin: Integrating Trust Assessment
// This would be in your Android app's trust evaluation module

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * TrustManager - Coordinates trust assessment with backend server
 */
class TrustManager(private val serverUrl: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    /**
     * Perform local pre-checks before calling the server.
     * Returns true if the device should proceed to server verification.
     */
    suspend fun performLocalPreCheck(): PreCheckResult = withContext(Dispatchers.IO) {
        val checks = mutableListOf<CheckResult>()

        // Check 1: Root detection
        checks.add(CheckResult(
            name = "root",
            passed = !isDeviceRooted(),
            details = if (isDeviceRooted()) "Device is rooted" else "No root detected"
        ))

        // Check 2: SafetyNet/Integrity API
        checks.add(CheckResult(
            name = "integrity",
            passed = true, // Call SafetyNet or Play Integrity here
            details = "Integrity check performed"
        ))

        // Check 3: Screen lock
        checks.add(CheckResult(
            name = "screen_lock",
            passed = hasScreenLock(),
            details = if (hasScreenLock()) "Screen lock enabled" else "No screen lock"
        ))

        // Check 4: Encryption
        checks.add(CheckResult(
            name = "encryption",
            passed = isDeviceEncrypted(),
            details = if (isDeviceEncrypted()) "Device encrypted" else "Encryption disabled"
        ))

        PreCheckResult(
            passed = checks.all { it.passed },
            checks = checks,
            shouldProceedToServer = checks.count { it.passed } >= checks.size / 2
        )
    }

    /**
     * Request server-side trust verification.
     * The server runs the full TrustScorer analysis.
     */
    suspend fun requestServerVerification(nonce: String): ServerVerificationResult {
        return withContext(Dispatchers.IO) {
            val requestBody = JSONObject().apply {
                put("nonce", nonce)
                put("device_info", getDeviceInfo())
            }.toString()

            val request = Request.Builder()
                .url("$serverUrl/api/v1/trust/verify")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .addHeader("X-API-Key", apiKey)
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val json = JSONObject(response.body?.string() ?: "{}")
                ServerVerificationResult(
                    verified = json.getBoolean("verified"),
                    score = json.getDouble("overall_score"),
                    trustLevel = json.getString("trust_level"),
                    failedChecks = json.getJSONArray("failed_checks").toList(),
                    recommendations = json.getJSONArray("recommendations").toList()
                )
            } else {
                throw TrustVerificationException("Server returned ${response.code}")
            }
        }
    }

    /**
     * Complete trust check workflow.
     */
    suspend fun performCompleteTrustCheck(): TrustCheckOutcome {
        val localResult = performLocalPreCheck()

        if (!localResult.shouldProceedToServer) {
            return TrustCheckOutcome(
                allowed = false,
                reason = TrustDenialReason.DEVICE_UNTRUSTED,
                message = "Local checks failed - device may be compromised"
            )
        }

        val nonce = generateServerNonce()
        return try {
            val serverResult = requestServerVerification(nonce)

            if (serverResult.verified) {
                TrustCheckOutcome(
                    allowed = true,
                    score = serverResult.score,
                    trustLevel = serverResult.trustLevel
                )
            } else {
                TrustCheckOutcome(
                    allowed = false,
                    reason = TrustDenialReason.FAILED_VERIFICATION,
                    message = "Server verification failed: ${serverResult.failedChecks.joinToString()}"
                )
            }
        } catch (e: Exception) {
            // On network failure, deny access for high-security operations
            TrustCheckOutcome(
                allowed = false,
                reason = TrustDenialReason.SERVER_UNREACHABLE,
                message = "Could not reach verification server: ${e.message}"
            )
        }
    }
}

// Data classes
data class CheckResult(val name: String, val passed: Boolean, val details: String)
data class PreCheckResult(val passed: Boolean, val checks: List<CheckResult>, val shouldProceedToServer: Boolean)
data class ServerVerificationResult(
    val verified: Boolean,
    val score: Double,
    val trustLevel: String,
    val failedChecks: List<String>,
    val recommendations: List<String>
)
data class TrustCheckOutcome(
    val allowed: Boolean,
    val reason: TrustDenialReason? = null,
    val message: String? = null,
    val score: Double? = null,
    val trustLevel: String? = null
)
enum class TrustDenialReason { DEVICE_UNTRUSTED, FAILED_VERIFICATION, SERVER_UNREACHABLE, RATE_LIMITED }
'''

if __name__ == "__main__":
    print("Kotlin Integration Example:")
    print("=" * 50)
    print(KOTLIN_EXAMPLE)
