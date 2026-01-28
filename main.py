from neura_ai import Neura, NeuraVoice
import pyfiglet

def main():
    print(pyfiglet.figlet_format("NEURA AI"))
    ai = Neura()
    voice = NeuraVoice()

    print("🤖 Neura Online. Digite algo ou 'voz' para falar.")

    while True:
        user_input = input("👤 Você: ").strip().lower()

        if user_input in ["sair", "exit"]:
            break
        
        if user_input == "voz":
            user_input = voice.listen()
            if not user_input: 
                continue
            print(f"🗣️ Você disse: {user_input}")

        ai.save_message("user", user_input)
        resposta = ai.get_response(user_input)
        
        print(f"🤖 Neura: {resposta}")
        ai.save_message("assistant", resposta)
        voice.speak(resposta)

if __name__ == "__main__":
    main()