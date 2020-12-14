package com.example.examplemod;

import net.minecraftforge.event.ServerChatEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.entity.passive.EntityWolf;
import net.minecraft.world.WorldServer;
import net.minecraft.world.storage.WorldInfo;
import java.util.UUID;

public class EventServerChat {
    @SubscribeEvent
    public void onServerChat(ServerChatEvent event) {
        System.out.format("[ONSERVERCHAT] %s: %s\n", event.getUsername(), event.getMessage());

        UUID playerUUID = EntityPlayer.getOfflineUUID(event.getUsername());
        System.out.format("Player UUID: %s\n", playerUUID.toString());
        WorldServer world = event.getPlayer().getServerWorld();
        System.out.format("\tFound world %s\n", world.getWorldInfo().getWorldName());
        EntityWolf wolf = WolfCommands.getSpecificWolf("Scout", world);
        if (wolf == null) {
            System.out.format("[ONSERVERCHAT] Did not find Scout\n");
            return;
        } 
        else {
            System.out.format("Scout's Owner ID: %s\n", wolf.getOwnerId().toString());
        }

        // take ownership of Scout
        wolf.setOwnerId(playerUUID);
        wolf.setTamed(true);

        String message = event.getMessage();
        if (message.equals("hello console")) {
            System.out.format("\thello player\n");
        }

        if (message.equals("follow")) {
            System.out.format("\tfollow\n");
            WolfCommands.followPlayer(wolf);
        }

        if (message.equals("sit")) {
            System.out.format("\tsit\n");
            WolfCommands.sit(wolf);
        }

        if (message.equals("go there")) {
            System.out.format("\tgo there\n");
            WolfCommands.goToWhereUserIsLooking(wolf);
        }
    }
}