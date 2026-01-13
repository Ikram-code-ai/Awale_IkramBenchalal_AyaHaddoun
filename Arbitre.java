import java.io.*;
import java.util.concurrent.*;

public class Arbitre {
    private static final int TIMEOUT_SECONDS = 2; // Timeout de 2 secondes comme demandé
    private static final int STARTUP_TIMEOUT_SECONDS = 10; // Timeout plus long pour le demarrage de l'exe

    public static void main(String[] args) throws Exception {
        // === COMMANDE POUR LANCER LE BOT ===
        
        // Option 1: Utiliser l'executable (pas besoin de Python!)
        String[] cmdA = {"player.exe", "Joueur1"};
        String[] cmdB = {"player.exe", "Joueur2"};
        
        // Option 2: Utiliser Python directement (pour le developpement)
        // String[] cmdA = {"python", "-u", "awale_game/player_adapter.py", "Joueur1"};
        // String[] cmdB = {"python", "-u", "awale_game/player_adapter.py", "Joueur2"};
        
        // On passe l'argument Joueur1 ou Joueur2 au bot
        // Joueur1 = trous impairs (1,3,5,7,9,11,13,15) = commence en premier
        // Joueur2 = trous pairs (2,4,6,8,10,12,14,16) = joue en second
        
        Process A = Runtime.getRuntime().exec(cmdA);
        Process B = Runtime.getRuntime().exec(cmdB);

        Joueur joueurA = new Joueur("A", A);
        Joueur joueurB = new Joueur("B", B);

        Joueur courant = joueurA;
        Joueur autre = joueurB;

        String coup = "START";
        int nbCoups = 0;
        boolean firstMoveA = true;
        boolean firstMoveB = true;
        
        while (true) {
            // Reception du coup de l'adversaire
            courant.receive(coup);
            
            // Timeout plus long pour le premier coup (demarrage de l'exe)
            int timeout;
            if (courant == joueurA && firstMoveA) {
                timeout = STARTUP_TIMEOUT_SECONDS;
                firstMoveA = false;
            } else if (courant == joueurB && firstMoveB) {
                timeout = STARTUP_TIMEOUT_SECONDS;
                firstMoveB = false;
            } else {
                timeout = TIMEOUT_SECONDS;
            }
            
            coup = courant.response(timeout);
            if (coup == null) {
                disqualifier(courant, "timeout");
                break;
            }
            nbCoups++;
            if (nbCoups == 400) {
                System.out.println("RESULT LIMIT");
                // Si la limite est atteinte, on arrete la boucle
                // ici on ajoute un break
                break;
            }
            // Validation du coup
            // ici on decommenter la validation du coup
            if (!coupValide(coup)) {
               disqualifier(courant, "coup invalide : " + coup);
               break;
            }

            System.out.println(courant.nom + " -> " + coup);
            // Fin de partie
            if (coup.contains("RESULT")) {
                System.out.println(coup);
                break;
            }
            // Changement de joueur
            Joueur tmp = courant;
            courant = autre;
            autre = tmp;
        }
        joueurA.destroy();
        joueurB.destroy();
        System.out.println("Fin.");
    }

    // ===============================
    // Validation du coup (ADAPTE pour 1-16 + R/B/TB/TR)
    // ===============================
    // ici on adapte la validation pour le format du jeu
    private static boolean coupValide(String coup) {
        if (coup == null) return false;
        if (coup.contains("RESULT")) return true; // Les messages RESULT sont valides comme fin de protocole
        // Format attendu: Nombre (1-16) suivi de code couleur (R, B, TR, TB)
        // Regex: ^\d{1,2}(R|B|TR|TB)$
        return coup.matches("^\\d{1,2}(R|B|TR|TB)$");
    }

    private static void disqualifier(Joueur j, String raison) {
        System.out.println("RESULT Joueur " + j.nom + " disqualifié (" + raison + ")");
    }

    // ===============================
    // Classe Joueur
    // ===============================
    static class Joueur {
        String nom;
        Process process;
        BufferedWriter in;
        BufferedReader out;
        ExecutorService executor = Executors.newSingleThreadExecutor();

        Joueur(String nom, Process p) {
            this.nom = nom;
            this.process = p;
            this.in = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
            this.out = new BufferedReader(new InputStreamReader(p.getInputStream()));
        }

        void receive(String msg) throws IOException {
            in.write(msg);
            in.newLine();
            in.flush();
        }
        String response(int timeoutSeconds) throws IOException {
            Future<String> future = executor.submit(() -> out.readLine());
            try {
                return future.get(timeoutSeconds, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                future.cancel(true);
                return null;
            } catch (Exception e) {
                return null;
            }
        }

        void destroy() {
            executor.shutdownNow();
            process.destroy();
        }
    }
}
