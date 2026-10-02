import re
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Ganti dengan Token Bot Anda dari @BotFather
TOKEN = "8637312221:AAEEQrqIyLI5wtjjdgLy7Mol_t8HabvTCMM"
bot = telebot.TeleBot(TOKEN)

# Penyimpanan data sementara
active_reservations = {}


@bot.message_handler(func=lambda message: "VIP MEMBER RESERVATION" in message.text)
def handle_vip_reservation(message):
  try:
    text = message.text

    nama_match = re.search(r"Nama\s*:\s*(.*)", text)
    tanggal_match = re.search(r"Tanggal\s*:\s*(.*)", text)
    jam_match = re.search(r"Jam\s*:\s*(.*)", text)
    treatment_match = re.search(r"Treatment\s*:\s*(.*)", text)

    nama = nama_match.group(1).strip() if nama_match else "-"
    tanggal = tanggal_match.group(1).strip() if tanggal_match else "-"
    jam = jam_match.group(1).strip() if jam_match else "-"
    treatment = treatment_match.group(1).strip() if treatment_match else "-"

    res_id = len(active_reservations) + 1
    active_reservations[res_id] = {
        "nama": nama,
        "tanggal": tanggal,
        "jam": jam,
        "treatment": treatment,
        "status": "Menunggu Konfirmasi",
    }

    markup = InlineKeyboardMarkup()
    btn_ready = InlineKeyboardButton(
        "🙋‍♀️ Saya Ready / Ambil Jadwal Ini", callback_data=f"ready_{res_id}"
    )
    markup.add(btn_ready)

    rekap_pesan = (
        f"🚨 **ANTRIAN & RESERVASI VIP BARU! (#{res_id})** 🚨\n\n"
        f"👤 **Nama:** {nama}\n"
        f"📅 **Tanggal / Jam:** {tanggal} | {jam}\n"
        f"💅 **Treatment:** {treatment}\n\n"
        f"👇 *Therapist, silakan klik tombol di bawah untuk mengambil jadwal ini:*"
    )

    bot.send_message(
        message.chat.id, rekap_pesan, parse_mode="Markdown", reply_markup=markup
    )

  except Exception as e:
    bot.reply_to(message, f"⚠️️ Gagal memproses format reservasi. Error: {e}")


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("ready_")
)
def callback_ready(call):
  try:
    res_id = int(call.data.split("_")[1])
    nama_therapist = call.from_user.first_name

    if res_id in active_reservations:
      active_reservations[res_id]["status"] = f"Confirmed ({nama_therapist})"
      data = active_reservations[res_id]

      sukses_text = (
          f"✨ **RESERVASI VIP #{res_id} TERKUNCI!** ✨\n\n"
          f"Pelanggan: **{data['nama']}**\n"
          f"Treatment: {data['treatment']} ({data['jam']})\n"
          f"👩‍⚕️ **Therapist Penanggung Jawab:** {nama_therapist} (Terkonfirmasi"
          " via Tombol ✅)\n\n"
          "_Jadwal resmi diambil._"
      )

      bot.edit_message_text(
          sukses_text,
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          parse_mode="Markdown",
      )
      bot.answer_callback_query(
          call.id, text=f"Berhasil mengambil jadwal #{res_id}!"
      )
    else:
      bot.answer_callback_query(
          call.id, text="❌ Data reservasi tidak ditemukan."
      )

  except Exception as e:
    bot.answer_callback_query(call.id, text=f"Terjadi kesalahan: {e}")


print("Bot Salon VIP aktif...")
bot.infinity_polling()
