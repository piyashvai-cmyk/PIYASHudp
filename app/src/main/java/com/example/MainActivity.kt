package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.example.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

enum class BotCategory(val key: String, val displayName: String, val subtitle: String) {
    LEVEL_2("2_level", "2 Level", "Standard Bot (Standby, Chat, Room & Ghost)"),
    LEVEL_3("3_level", "3 Level", "Auto Match Pump (Continuous Lone Wolf 5.7s)")
}

enum class BotStatus {
    IDLE, STARTING, RUNNING, STOPPED, CRASHED
}

data class BotAccount(
    val id: String,
    val category: BotCategory,
    val uid: Long,
    val password: String,
    val name: String,
    var status: BotStatus = BotStatus.STOPPED,
    val logs: MutableList<String> = mutableListOf()
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                Scaffold(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(CyberDarkBg),
                    containerColor = CyberDarkBg,
                    contentWindowInsets = WindowInsets.safeDrawing
                ) { innerPadding ->
                    PanelDashboardScreen(modifier = Modifier.padding(innerPadding))
                }
            }
        }
    }
}

@Composable
fun PanelDashboardScreen(modifier: Modifier = Modifier) {
    val coroutineScope = rememberCoroutineScope()
    var selectedCategory by remember { mutableStateOf(BotCategory.LEVEL_2) }
    var showCreateDialog by remember { mutableStateOf(false) }
    var activeLogAccount by remember { mutableStateOf<BotAccount?>(null) }

    // Seeded accounts with user's configurations
    val accounts = remember {
        mutableStateListOf(
            BotAccount(
                id = "acc-1",
                category = BotCategory.LEVEL_2,
                uid = 794006L,
                password = "MARUF",
                name = "M4RUF Standard Bot",
                status = BotStatus.STOPPED,
                logs = mutableListOf("[INIT] 2 Level worker configuration loaded")
            ),
            BotAccount(
                id = "acc-2",
                category = BotCategory.LEVEL_3,
                uid = 4752927952L,
                password = "PIYASH_KVYDC_BY_STAR_GMR_FL7HG",
                name = "PIYASH Lone Wolf Pump",
                status = BotStatus.STOPPED,
                logs = mutableListOf("[INIT] 3 Level pump configuration loaded")
            )
        )
    }

    val totalAccounts = accounts.size
    val runningAccounts = accounts.count { it.status == BotStatus.RUNNING }
    val l2Running = accounts.count { it.category == BotCategory.LEVEL_2 && it.status == BotStatus.RUNNING }
    val l3Running = accounts.count { it.category == BotCategory.LEVEL_3 && it.status == BotStatus.RUNNING }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp)
    ) {
        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(NeonCyan)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "PIYASH LEVEL UP",
                        color = TextPrimary,
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        modifier = Modifier.testTag("app_title")
                    )
                }
                Text(
                    text = "Cloud Automation Core (Railway & GitHub Ready)",
                    color = TextSecondary,
                    fontSize = 12.sp,
                    fontFamily = FontFamily.Monospace
                )
            }

            Surface(
                shape = RoundedCornerShape(16.dp),
                color = CyberCardBg,
                border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    PulsingStatusDot(isRunning = runningAccounts > 0)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (runningAccounts > 0) "$runningAccounts ACTIVE" else "STANDBY",
                        color = if (runningAccounts > 0) NeonGreen else TextMuted,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Quick Stats Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            StatCard(title = "TOTAL", value = "$totalAccounts", modifier = Modifier.weight(1f))
            StatCard(title = "ACTIVE", value = "$runningAccounts", valueColor = NeonGreen, modifier = Modifier.weight(1f))
            StatCard(title = "2 LEVEL", value = "$l2Running", valueColor = NeonCyan, modifier = Modifier.weight(1f))
            StatCard(title = "3 LEVEL", value = "$l3Running", valueColor = NeonPurple, modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Category Tabs
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(CyberCardBg)
                .border(1.dp, CyberBorder, RoundedCornerShape(12.dp))
                .padding(4.dp)
        ) {
            BotCategory.values().forEach { cat ->
                val isSelected = selectedCategory == cat
                val tabCount = accounts.count { it.category == cat }
                val activeCount = accounts.count { it.category == cat && it.status == BotStatus.RUNNING }

                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(8.dp))
                        .then(
                            if (isSelected) {
                                Modifier.background(
                                    Brush.horizontalGradient(
                                        listOf(NeonCyan.copy(alpha = 0.25f), NeonPurple.copy(alpha = 0.25f))
                                    )
                                )
                            } else {
                                Modifier.background(Color.Transparent)
                            }
                        )
                        .border(
                            width = if (isSelected) 1.dp else 0.dp,
                            color = if (isSelected) NeonCyan else Color.Transparent,
                            shape = RoundedCornerShape(8.dp)
                        )
                        .clickable { selectedCategory = cat }
                        .padding(vertical = 10.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = cat.displayName,
                            color = if (isSelected) TextPrimary else TextSecondary,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                            fontSize = 14.sp
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Surface(
                            shape = CircleShape,
                            color = if (isSelected) NeonCyan.copy(alpha = 0.3f) else CyberBorder
                        ) {
                            Text(
                                text = "$activeCount/$tabCount",
                                color = if (isSelected) NeonCyan else TextMuted,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Category Banner and Create Button
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "${selectedCategory.displayName} Accounts",
                    color = TextPrimary,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = selectedCategory.subtitle,
                    color = TextSecondary,
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace
                )
            }

            Button(
                onClick = { showCreateDialog = true },
                colors = ButtonDefaults.buttonColors(containerColor = NeonCyan),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier
                    .testTag("create_account_button")
                    .height(38.dp)
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add", tint = Color.Black, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Create Account", color = Color.Black, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Accounts List
        val filteredAccounts = accounts.filter { it.category == selectedCategory }

        if (filteredAccounts.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .clip(RoundedCornerShape(12.dp))
                    .background(CyberCardBg)
                    .border(1.dp, CyberBorder, RoundedCornerShape(12.dp))
                    .padding(24.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.SmartToy,
                        contentDescription = "Empty",
                        tint = TextMuted,
                        modifier = Modifier.size(48.dp)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "No accounts configured in ${selectedCategory.displayName}",
                        color = TextMuted,
                        fontSize = 13.sp,
                        fontFamily = FontFamily.Monospace
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    OutlinedButton(
                        onClick = { showCreateDialog = true },
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = NeonCyan)
                    ) {
                        Text("Add First Account")
                    }
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(filteredAccounts, key = { it.id }) { acc ->
                    AccountCardItem(
                        account = acc,
                        onToggleStart = {
                            if (acc.status == BotStatus.RUNNING) {
                                acc.status = BotStatus.STOPPED
                                acc.logs.add("[${currentTime()}] Process stopped by user")
                            } else {
                                acc.status = BotStatus.STARTING
                                acc.logs.add("[${currentTime()}] Initializing ${acc.category.displayName} session for UID ${acc.uid}...")
                                coroutineScope.launch {
                                    delay(1200)
                                    acc.status = BotStatus.RUNNING
                                    acc.logs.add("[${currentTime()}] Handshake verified. Online socket connected.")
                                    if (acc.category == BotCategory.LEVEL_3) {
                                        acc.logs.add("[${currentTime()}] [PUMP] Lone Wolf queue injection active (5.7s loop)")
                                    }
                                }
                            }
                        },
                        onOpenLogs = { activeLogAccount = acc },
                        onDelete = {
                            accounts.remove(acc)
                        }
                    )
                }

                // GitHub / Railway Sync Footer
                item {
                    Spacer(modifier = Modifier.height(8.dp))
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        color = CyberCardBg,
                        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Default.CloudSync, contentDescription = "Sync", tint = NeonPurple, modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = "Railway.app & GitHub Sync",
                                    color = TextPrimary,
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "server.py, level2_worker.py & level3_worker.py are configured. Export to GitHub from settings to deploy.",
                                    color = TextSecondary,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    // Create Account Dialog
    if (showCreateDialog) {
        CreateAccountDialog(
            category = selectedCategory,
            onDismiss = { showCreateDialog = false },
            onCreate = { uid, pass, name, autoStart ->
                val newAcc = BotAccount(
                    id = "acc-${System.currentTimeMillis()}",
                    category = selectedCategory,
                    uid = uid,
                    password = pass,
                    name = name.ifBlank { "Bot-$uid" },
                    status = if (autoStart) BotStatus.STARTING else BotStatus.STOPPED,
                    logs = mutableListOf("[${currentTime()}] Account created under ${selectedCategory.displayName}")
                )
                accounts.add(newAcc)
                if (autoStart) {
                    coroutineScope.launch {
                        delay(1000)
                        newAcc.status = BotStatus.RUNNING
                        newAcc.logs.add("[${currentTime()}] Connected successfully.")
                        if (newAcc.category == BotCategory.LEVEL_3) {
                            newAcc.logs.add("[${currentTime()}] [PUMP] 5.7s Lone Wolf injection cycle started.")
                        }
                    }
                }
                showCreateDialog = false
            }
        )
    }

    // Live Logs Dialog
    activeLogAccount?.let { acc ->
        TerminalLogsDialog(
            account = acc,
            onDismiss = { activeLogAccount = null }
        )
    }
}

@Composable
fun StatCard(title: String, value: String, valueColor: Color = TextPrimary, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        color = CyberCardBg,
        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Text(text = title, color = TextMuted, fontSize = 9.sp, fontFamily = FontFamily.Monospace)
            Spacer(modifier = Modifier.height(2.dp))
            Text(text = value, color = valueColor, fontSize = 18.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
        }
    }
}

@Composable
fun AccountCardItem(
    account: BotAccount,
    onToggleStart: () -> Unit,
    onOpenLogs: () -> Unit,
    onDelete: () -> Unit
) {
    val isRunning = account.status == BotStatus.RUNNING
    val borderCol by animateColorAsState(
        if (isRunning) NeonGreen.copy(alpha = 0.5f) else CyberBorder
    )

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .testTag("account_card_${account.id}"),
        shape = RoundedCornerShape(12.dp),
        color = CyberCardBg,
        border = androidx.compose.foundation.BorderStroke(1.dp, borderCol)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(text = account.name, color = TextPrimary, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text(text = "UID: ${account.uid}", color = TextSecondary, fontSize = 12.sp, fontFamily = FontFamily.Monospace)
                }

                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = when (account.status) {
                        BotStatus.RUNNING -> NeonGreen.copy(alpha = 0.15f)
                        BotStatus.STARTING -> NeonAmber.copy(alpha = 0.15f)
                        else -> CyberBorder
                    },
                    border = androidx.compose.foundation.BorderStroke(
                        1.dp,
                        when (account.status) {
                            BotStatus.RUNNING -> NeonGreen
                            BotStatus.STARTING -> NeonAmber
                            else -> TextMuted
                        }
                    )
                ) {
                    Text(
                        text = account.status.name,
                        color = when (account.status) {
                            BotStatus.RUNNING -> NeonGreen
                            BotStatus.STARTING -> NeonAmber
                            else -> TextMuted
                        },
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Surface(
                shape = RoundedCornerShape(6.dp),
                color = CyberDarkBg,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "CATEGORY: ${account.category.displayName}", color = TextSecondary, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                    Text(text = "PASS: ••••••••", color = TextMuted, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onToggleStart,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isRunning) NeonRed.copy(alpha = 0.2f) else NeonGreen.copy(alpha = 0.2f),
                        contentColor = if (isRunning) NeonRed else NeonGreen
                    ),
                    shape = RoundedCornerShape(6.dp),
                    modifier = Modifier
                        .weight(1f)
                        .height(34.dp)
                        .testTag("toggle_btn_${account.id}")
                ) {
                    Icon(
                        imageVector = if (isRunning) Icons.Default.Stop else Icons.Default.PlayArrow,
                        contentDescription = if (isRunning) "Stop" else "Start",
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(if (isRunning) "Stop" else "Start", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }

                OutlinedButton(
                    onClick = onOpenLogs,
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = NeonPurple),
                    shape = RoundedCornerShape(6.dp),
                    modifier = Modifier
                        .weight(1f)
                        .height(34.dp)
                        .testTag("logs_btn_${account.id}")
                ) {
                    Icon(Icons.Default.Terminal, contentDescription = "Logs", modifier = Modifier.size(14.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Logs", fontSize = 12.sp)
                }

                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.size(34.dp)
                ) {
                    Icon(Icons.Default.DeleteOutline, contentDescription = "Delete", tint = TextMuted, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}

@Composable
fun CreateAccountDialog(
    category: BotCategory,
    onDismiss: () -> Unit,
    onCreate: (Long, String, String, Boolean) -> Unit
) {
    var uidText by remember { mutableStateOf("") }
    var passwordText by remember { mutableStateOf("") }
    var nameText by remember { mutableStateOf("") }
    var isPasswordVisible by remember { mutableStateOf(false) }
    var autoStart by remember { mutableStateOf(true) }
    var hasError by remember { mutableStateOf(false) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = CyberCardBg,
            border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(text = "Create a New Account", color = TextPrimary, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Text(text = "Target Category: ${category.displayName}", color = NeonCyan, fontSize = 12.sp, fontFamily = FontFamily.Monospace)

                Spacer(modifier = Modifier.height(14.dp))

                OutlinedTextField(
                    value = uidText,
                    onValueChange = { uidText = it; hasError = false },
                    label = { Text("UID (Account ID)") },
                    placeholder = { Text("e.g. 794006 or 4752927952") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = NeonCyan,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("input_uid")
                )

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedTextField(
                    value = passwordText,
                    onValueChange = { passwordText = it; hasError = false },
                    label = { Text("Password / Secret") },
                    placeholder = { Text("e.g. MARUF") },
                    singleLine = true,
                    visualTransformation = if (isPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    trailingIcon = {
                        IconButton(onClick = { isPasswordVisible = !isPasswordVisible }) {
                            Icon(
                                if (isPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                contentDescription = "Toggle password",
                                tint = TextMuted
                            )
                        }
                    },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = NeonCyan,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("input_password")
                )

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedTextField(
                    value = nameText,
                    onValueChange = { nameText = it },
                    label = { Text("Custom Name (Bot Owner)") },
                    placeholder = { Text("e.g. Piyash Worker") },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = NeonCyan,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("input_name")
                )

                Spacer(modifier = Modifier.height(10.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = autoStart,
                        onCheckedChange = { autoStart = it },
                        colors = CheckboxDefaults.colors(checkedColor = NeonCyan)
                    )
                    Text("Start process immediately", color = TextSecondary, fontSize = 12.sp)
                }

                if (hasError) {
                    Text("Please enter a valid numeric UID and password", color = NeonRed, fontSize = 11.sp)
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextButton(onClick = onDismiss) {
                        Text("Cancel", color = TextMuted)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(
                        onClick = {
                            val parsedUid = uidText.trim().toLongOrNull()
                            val pass = passwordText.trim()
                            if (parsedUid != null && pass.isNotEmpty()) {
                                onCreate(parsedUid, pass, nameText.trim(), autoStart)
                            } else {
                                hasError = true
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = NeonCyan),
                        modifier = Modifier.testTag("dialog_submit_button")
                    ) {
                        Text("Start Account", color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun TerminalLogsDialog(account: BotAccount, onDismiss: () -> Unit) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = Color(0xFF040711),
            border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder),
            modifier = Modifier
                .fillMaxWidth()
                .height(420.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = "LIVE TERMINAL: ${account.name}", color = TextPrimary, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        Text(text = "UID: ${account.uid} | ${account.category.displayName}", color = NeonCyan, fontSize = 11.sp, fontFamily = FontFamily.Monospace)
                    }
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close", tint = TextMuted)
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0xFF000208))
                        .border(1.dp, Color(0xFF1E293B), RoundedCornerShape(8.dp))
                        .padding(10.dp)
                ) {
                    LazyColumn(modifier = Modifier.fillMaxSize()) {
                        items(account.logs) { line ->
                            Text(
                                text = line,
                                color = when {
                                    line.contains("ERROR", true) -> NeonRed
                                    line.contains("PUMP", true) -> NeonPurple
                                    line.contains("Online", true) || line.contains("Connected", true) -> NeonGreen
                                    else -> TextSecondary
                                },
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(NeonGreen))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Stream Active", color = TextMuted, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                    }
                    TextButton(onClick = { account.logs.clear(); account.logs.add("[${currentTime()}] Log cleared") }) {
                        Text("Clear View", color = TextMuted, fontSize = 11.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun PulsingStatusDot(isRunning: Boolean) {
    val infiniteTransition = rememberInfiniteTransition()
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.4f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        )
    )

    Box(
        modifier = Modifier
            .size(8.dp)
            .clip(CircleShape)
            .background(if (isRunning) NeonGreen.copy(alpha = alpha) else TextMuted)
    )
}

fun currentTime(): String {
    return SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
}
