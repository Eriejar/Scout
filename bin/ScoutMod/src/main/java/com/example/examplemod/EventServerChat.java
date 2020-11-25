package com.example.examplemod;

import net.minecraftforge.event.ServerChatEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.entity.passive.EntityWolf;
import net.minecraft.world.WorldServer;
import net.minecraft.world.storage.WorldInfo;

public class EventServerChat {
    @SubscribeEvent
    public void onServerChat(ServerChatEvent event) {
        System.out.format("CHAT EVENT| %s: %s\n", event.getUsername(), event.getMessage());

        WorldServer world = event.getPlayer().getServerWorld();
        System.out.format("Found world %s\n", world.getWorldInfo().getWorldName());
        EntityWolf wolf = WolfCommands.getSpecificWolf("Scout", world);


        String message = event.getMessage();
        if (message.equals("hello console")) {
            System.out.format("hello player\n");
        }

        if (message.equals("follow")) {
            System.out.format("follow me\n");
            WolfCommands.followPlayer(wolf);
        }

        if (message.equals("sit")) {
            System.out.format("sit\n");
            WolfCommands.sit(wolf);
        }
    }
}